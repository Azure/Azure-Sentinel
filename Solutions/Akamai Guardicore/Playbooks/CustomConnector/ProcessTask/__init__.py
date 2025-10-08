import asyncio
import datetime
import logging
import json

from azure.core import MatchConditions

from .utils.import_logic import run_import_loop
from ..generic_utilities.connection_slot_marker import ConnectionSlotMarker, SlotStatus


def main(name: str) -> dict:
    """
    Azure Function to process a task.
    Accepts task data, processes it, and marks it as COMPLETED.
    """
    task_data = json.loads(name)
    try:
        logging.info(f"ProcessTask function started for task: {task_data.get('partition_key')}/{task_data.get('row_key')}")

        slot_marker = ConnectionSlotMarker()
        table_client = slot_marker.table_service.get_table_client(slot_marker.table_name)

        partition_key = task_data['partition_key']
        row_key = task_data['row_key']

        current_entity = table_client.get_entity(
            partition_key=partition_key,
            row_key=row_key
        )
        current_etag = current_entity.metadata['etag']
        if current_entity.get('status') != SlotStatus.IN_PROGRESS.value:
            logging.warning(f"Task {partition_key}/{row_key} is no longer in IN_PROGRESS state. Current status: {current_entity.get('status')}")
            return {"status": "skipped", "reason": "Task no longer in progress"}

        logging.info(f"Processing task for time slot: {task_data.get('slot_start')}")
        logging.info(f"Processing IPs: {task_data.get('ips')}")
        logging.info(f"Processing event IDs: {task_data.get('event_ids')}")

        slot_start_time = datetime.datetime.fromisoformat(task_data.get('slot_start'))
        slot_end_time = slot_start_time + datetime.timedelta(minutes=5)

        ips = task_data['ips']
        params = {
                    'from_time': int(slot_start_time.timestamp() * 1000),
                    'to_time': int(slot_end_time.timestamp() * 1000),
                    'sort': 'slot_start_time'
                }
        if ips:
            params['any_side_subnet'] = f"{','.join([f'{ip}/32' for ip in ips])}"
        slot_id = f"{current_entity['PartitionKey']}_{current_entity['RowKey']}"
        asyncio.run(
            run_import_loop(
                destination_table='GuardicoreEnrichingConnections',
                api_endpoint='api/v3.0/connections',
                method='GET',
                params=params,
                slot_identifier=slot_id,
                chunk_size=4000,
            )
        )

        updated_entity = dict(current_entity)
        updated_entity['status'] = SlotStatus.COMPLETED.value
        updated_entity['last_updated'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        updated_entity['completed_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        table_client.update_entity(
            updated_entity,
            mode='replace',
            match_condition=MatchConditions.IfNotModified,
            etag=current_etag
        )

        logging.info(f"Successfully completed task: {partition_key}/{row_key}")

        return {
            "status": "completed",
            "partition_key": partition_key,
            "row_key": row_key,
            "completed_at": updated_entity['completed_at'],
        }

    except Exception as e:
        logging.error(f"Error in ProcessTask: {str(e)}")
        raise