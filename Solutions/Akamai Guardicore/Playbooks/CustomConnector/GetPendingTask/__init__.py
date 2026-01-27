import datetime
import logging
from ..generic_utilities.connection_slot_marker import ConnectionSlotMarker, SlotStatus


def main(name: str) -> dict | None:
    """
    Azure Function to get a pending task for processing.
    Returns a task that is in PENDING, RETRY, or IN_PROGRESS state for more than 1 hour.
    """
    try:
        logging.info("GetPendingTask function started")
        
        # Initialize the connection slot marker
        slot_marker = ConnectionSlotMarker()
        
        # First, try to get a PENDING task
        task = slot_marker.get_and_mark_slot(
            source_status=SlotStatus.PENDING,
            target_status=SlotStatus.IN_PROGRESS
        )
        
        if task:
            # Add processing_started timestamp
            task['processing_started'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            logging.info(f"Found PENDING task: {task['partition_key']}/{task['row_key']}")
            return task
        
        # If no PENDING tasks, try RETRY tasks
        task = slot_marker.get_and_mark_slot(
            source_status=SlotStatus.RETRY,
            target_status=SlotStatus.IN_PROGRESS
        )
        
        if task:
            task['processing_started'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            logging.info(f"Found RETRY task: {task['partition_key']}/{task['row_key']}")
            return task
        
        # Finally, check for IN_PROGRESS tasks that are older than 1 hour
        # This will be handled by a custom method since we need different logic
        stale_task = slot_marker.get_and_mark_slot(
            source_status=SlotStatus.IN_PROGRESS,
            target_status=SlotStatus.IN_PROGRESS,
            not_updated_for=datetime.timedelta(hours=1)  # Only consider tasks older than 1 hour
        )
        if stale_task:
            logging.info(f"Found stale IN_PROGRESS task: {stale_task['partition_key']}/{stale_task['row_key']}")
            return stale_task
        
        logging.info("No pending tasks found")
        return None
        
    except Exception as e:
        logging.error(f"Error in GetPendingTask: {str(e)}")
        raise

