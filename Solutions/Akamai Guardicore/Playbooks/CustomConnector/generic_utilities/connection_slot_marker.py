import datetime
import hashlib
import json
import logging
import os
from enum import Enum

from azure.core import MatchConditions
from azure.core.exceptions import ResourceExistsError
from azure.data.tables import TableServiceClient


class SlotStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class ConnectionSlotMarker:
    def __init__(self, connection_string: str | None = None):
        """
        Initialize the deduplicator with Azure Storage connection

        Args:
            connection_string: Azure Storage connection string. If None, will try to get from environment
        """
        self.connection_string = connection_string or os.environ.get('AzureWebJobsStorage')
        if not self.connection_string:
            raise ValueError("Azure Storage connection string not provided")

        self.table_service = TableServiceClient.from_connection_string(self.connection_string)
        self.table_name = "GuardicoreConnectionSlots"
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Create the deduplication table if it doesn't exist"""
        try:
            self.table_service.create_table(self.table_name)
            logging.info(f"Created deduplication table: {self.table_name}")
        except ResourceExistsError:
            logging.debug(f"Deduplication table already exists: {self.table_name}")
        except Exception as e:
            logging.error(f"Error creating deduplication table: {str(e)}")
            raise

    @staticmethod
    def _get_unique_hash(ips: set[str]) -> str:
        ips_list = sorted(list(ips))
        json_str = json.dumps({'ips': ips_list}, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    @staticmethod
    def _get_relevant_time_slots(event_time: datetime.datetime) -> list[datetime.datetime]:
        """
        Get the relevant time slots for a given event time.
        This will return the 5-minute slots before and after the event time.
        """
        slots = []
        for i in range(-1, 2):
            slot_time = event_time + datetime.timedelta(minutes=i * 5)
            minutes = (slot_time.minute // 5) * 5
            slot_start = slot_time.replace(minute=minutes, second=0, microsecond=0)
            slots.append(slot_start)
        return slots

    @staticmethod
    def _generate_partition_key(slot_start: datetime) -> str:
        """Generate partition key from time slot for efficient querying"""
        return slot_start.strftime("%Y%m%d%H%M")

    def mark_slot_for_fetching(self, event_time: datetime.datetime, ips: set[str]) -> list[dict[str, str]]:
        """
        Mark time slots for fetching by creating or updating slot entities
        Returns list of slot identifiers for posting to Sentinel

        Args:
            event_time: When the event occurred
            ips: Set of IP addresses involved in the event

        Returns:
            List of slot identifiers with partition_key and row_key
        """
        uniqueness_hash = self._get_unique_hash(ips)
        time_slots = self._get_relevant_time_slots(event_time)
        table_client = self.table_service.get_table_client(self.table_name)

        slot_identifiers = []

        for slot in time_slots:
            partition_key = self._generate_partition_key(slot)
            row_key = uniqueness_hash

            slot_id = f"{partition_key}_{row_key}"
            slot_identifiers.append({
                "slot_id": slot_id,
                "partition_key": partition_key,
                "row_key": row_key
            })

            max_retries = 5
            for attempt in range(max_retries):
                try:
                    try:
                        existing_entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)
                        # Entity exists, just update the last_updated timestamp
                        etag = existing_entity.metadata['etag']

                        entity = {
                            'PartitionKey': partition_key,
                            'RowKey': row_key,
                            'slot_start': slot.isoformat(),
                            'ips': json.dumps(sorted(list(ips))),
                            'status': existing_entity.get('status', SlotStatus.PENDING.value),
                            'last_updated': datetime.datetime.now(datetime.timezone.utc).isoformat()
                        }

                        table_client.update_entity(entity, mode='replace',
                                                   match_condition=MatchConditions.IfNotModified, etag=etag)
                        logging.debug(f"Updated existing slot {slot_id}")
                        break

                    except Exception as get_error:
                        if "ResourceNotFound" in str(get_error):
                            # Create new entity
                            entity = {
                                'PartitionKey': partition_key,
                                'RowKey': row_key,
                                'slot_start': slot.isoformat(),
                                'ips': json.dumps(sorted(list(ips))),
                                'status': SlotStatus.PENDING.value,
                                'created': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                'last_updated': datetime.datetime.now(datetime.timezone.utc).isoformat()
                            }

                            try:
                                table_client.create_entity(entity)
                                logging.debug(f"Created new slot {slot_id}")
                                break
                            except ResourceExistsError:
                                logging.debug(f"Slot {slot_id} was created by another process, retrying")
                                continue
                        else:
                            raise get_error

                except Exception as update_error:
                    if "UpdateConditionNotSatisfied" in str(update_error) or "PreconditionFailed" in str(update_error):
                        # ETag mismatch, someone else updated it, retry
                        logging.debug(f"Concurrent update detected for slot {slot_id}, retrying (attempt {attempt + 1})")
                        if attempt == max_retries - 1:
                            logging.error(f"Failed to update slot {slot_id} after {max_retries} attempts")
                            raise Exception(f"Maximum retry attempts exceeded for slot {slot_id}")
                        continue
                    else:
                        logging.error(f"Error updating slot {slot_id}: {str(update_error)}")
                        raise

        return slot_identifiers

    def get_and_mark_slot(self, source_status: SlotStatus = SlotStatus.PENDING,
                          target_status: SlotStatus = SlotStatus.IN_PROGRESS,
                          not_updated_for: datetime.timedelta | None = None) -> dict | None:
        table_client = self.table_service.get_table_client(self.table_name)

        cutoff_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)

        try:
            query_filter = f"status eq '{source_status.value}'"

            entities = table_client.query_entities(
                query_filter=query_filter,
                select=["PartitionKey", "RowKey", "slot_start", "ips", "status", "last_updated"]
            )

            for entity in entities:
                try:
                    slot_start = datetime.datetime.fromisoformat(entity['slot_start'])
                    if slot_start > cutoff_time:
                        continue

                    current_entity = table_client.get_entity(
                        partition_key=entity['PartitionKey'],
                        row_key=entity['RowKey']
                    )
                    entity_etag = current_entity.metadata['etag']
                    if current_entity.get('status') != source_status.value:
                        continue

                    current_slot_start = datetime.datetime.fromisoformat(current_entity['slot_start'])
                    if current_slot_start > cutoff_time:
                        continue

                    # Double-check the not_updated_for condition with the current entity
                    if not_updated_for is not None:
                        current_last_updated = datetime.datetime.fromisoformat(current_entity['last_updated'])
                        min_last_updated_time = datetime.datetime.now(datetime.timezone.utc) - not_updated_for
                        if current_last_updated > min_last_updated_time:
                            continue

                    updated_entity = dict(current_entity)
                    updated_entity['status'] = target_status.value
                    updated_entity['last_updated'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

                    table_client.update_entity(
                        updated_entity,
                        mode='replace',
                        match_condition=MatchConditions.IfNotModified,
                        etag=entity_etag
                    )

                    logging.info(
                        f"Successfully marked slot {entity['PartitionKey']}/{entity['RowKey']} from {source_status.value} to {target_status.value}")

                    return {
                        'partition_key': updated_entity['PartitionKey'],
                        'row_key': updated_entity['RowKey'],
                        'slot_id': f"{updated_entity['PartitionKey']}_{updated_entity['RowKey']}",
                        'slot_start': updated_entity['slot_start'],
                        'ips': json.loads(updated_entity['ips']),
                        'status': updated_entity['status'],
                        'last_updated': updated_entity['last_updated'],
                        'processing_started': updated_entity.get('processing_started')
                    }

                except Exception as e:
                    if "UpdateConditionNotSatisfied" in str(e) or "PreconditionFailed" in str(e):
                        logging.debug(
                            f"Concurrent update detected for slot {entity['PartitionKey']}/{entity['RowKey']}, trying next slot")
                        continue
                    elif "ResourceNotFound" in str(e):
                        logging.debug(
                            f"Entity {entity['PartitionKey']}/{entity['RowKey']} was deleted, trying next slot")
                        continue
                    else:
                        logging.warning(f"Error processing slot {entity['PartitionKey']}/{entity['RowKey']}: {str(e)}")
                        continue

            logging.debug(f"No eligible {source_status.value} slots found that are at least 5 minutes old")
            return None

        except Exception as e:
            logging.error(f"Error querying for {source_status.value} slots: {str(e)}")
            raise
