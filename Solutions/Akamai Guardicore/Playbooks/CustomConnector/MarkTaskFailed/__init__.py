import datetime
import logging
import json

from azure.core import MatchConditions

from ..generic_utilities.connection_slot_marker import ConnectionSlotMarker, SlotStatus


def main(name: str) -> dict:
    """
    Azure Function to mark a task as failed.
    Called when ProcessTask throws an exception.
    """
    task_data = json.loads(name)
    try:
        logging.info(f"MarkTaskFailed function started for task: {task_data.get('partition_key')}/{task_data.get('row_key')}")

        slot_marker = ConnectionSlotMarker()
        table_client = slot_marker.table_service.get_table_client(slot_marker.table_name)

        partition_key = task_data['partition_key']
        row_key = task_data['row_key']

        current_entity = table_client.get_entity(
            partition_key=partition_key,
            row_key=row_key
        )
        current_etag = current_entity.metadata['etag']
        logging.info(f"Marking task {partition_key}/{row_key} as FAILED")

        updated_entity = dict(current_entity)
        updated_entity['status'] = SlotStatus.FAILED.value
        updated_entity['last_updated'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        updated_entity['failed_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        error_info = task_data.get('error_info')
        if error_info:
            updated_entity['last_error'] = json.dumps({
                "error": str(error_info),
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })

        table_client.update_entity(
            updated_entity,
            mode='replace',
            match_condition=MatchConditions.IfNotModified,
            etag=current_etag
        )

        result_message = f"Task {partition_key}/{row_key} marked as FAILED"
        logging.info(result_message)

        return {
            "status": SlotStatus.FAILED.value,
            "partition_key": partition_key,
            "row_key": row_key,
            "updated_at": updated_entity['last_updated'],
            "failed_at": updated_entity['failed_at']
        }

    except Exception as e:
        logging.error(f"Error in MarkTaskFailed: {str(e)}")
        raise
