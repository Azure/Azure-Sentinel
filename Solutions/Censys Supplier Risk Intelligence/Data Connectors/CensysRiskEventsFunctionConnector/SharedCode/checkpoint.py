"""Checkpoint of the last ingested risk event, stored in an Azure Storage Table."""
import datetime
import hashlib
from typing import Optional, Tuple

from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableServiceClient, UpdateMode

from .consts import CHECKPOINT_PARTITION_KEY, LOG_PREFIX
from .exceptions import CensysException
from .logger import applogger


def checkpoint_key(*parts: str) -> str:
    """Build a stable row key from the settings that define what is collected.

    A different organization, supplier list or filter set gets its own checkpoint, so changing
    the configuration never skips events.
    """
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:32]


class CheckpointManager:
    """Reads and writes the (inserted_at, event_id) checkpoint."""

    def __init__(self, connection_string: str, table_name: str):
        """Create the table client, creating the table when needed."""
        self.table_name = table_name
        try:
            service = TableServiceClient.from_connection_string(conn_str=connection_string)
            self.table = service.create_table_if_not_exists(table_name)
        except Exception as err:
            applogger.error(f"{LOG_PREFIX}: error accessing checkpoint table {table_name}: {err}")
            raise CensysException(f"Error accessing checkpoint table {table_name}: {err}")

    def get(self, row_key: str) -> Optional[Tuple[str, str]]:
        """Return (inserted_at, event_id) or None when no checkpoint exists."""
        try:
            entity = self.table.get_entity(partition_key=CHECKPOINT_PARTITION_KEY, row_key=row_key)
            return entity.get("InsertedAt"), entity.get("EventId")
        except ResourceNotFoundError:
            return None
        except Exception as err:
            applogger.error(f"{LOG_PREFIX}: error reading checkpoint: {err}")
            raise CensysException(f"Error reading checkpoint: {err}")

    def set(self, row_key: str, inserted_at: str, event_id: str) -> None:
        """Store the inserted_at and id of the last event that was ingested."""
        entity = {
            "PartitionKey": CHECKPOINT_PARTITION_KEY,
            "RowKey": row_key,
            "InsertedAt": inserted_at,
            "EventId": event_id,
            "UpdatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        try:
            self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=entity)
        except Exception as err:
            applogger.error(f"{LOG_PREFIX}: error saving checkpoint: {err}")
            raise CensysException(f"Error saving checkpoint: {err}")
