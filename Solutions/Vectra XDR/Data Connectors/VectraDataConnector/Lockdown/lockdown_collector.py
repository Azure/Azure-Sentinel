"""This lockdown_collector file will pull and push the data of lockdown."""
from ..SharedCode.collector import BaseCollector
from ..SharedCode.state_manager import StateManager
from ..SharedCode.consts import LOCKDOWN_TABLE_NAME, LOCKDOWN_ENDPOINT

HASH_FIELD_LIST = ["entity_name", "entity_type", "lock_event_timestamp", "unlock_event_timestamp"]

class LockdownCollector(BaseCollector):
    """This class contains methods to create object, get checkpoint and call 'pull and push the snapshot data'method."""

    def __init__(self, applogger, function_name, client_id, client_secret) -> None:
        """Initialize instance variable for class."""
        super(LockdownCollector, self).__init__(applogger, function_name, client_id, client_secret)
        self.lockdown_table_name = LOCKDOWN_TABLE_NAME

    def get_lockdown_data_and_ingest_into_sentinel(self):
        """To call get checkpoint and 'pull and push the data' method for lockdown data."""
        self.state = StateManager(
            connection_string=self.connection_string, file_path="lockdown"
        )
        hashed_events_list = self.get_checkpoint_snapshot()
        self.pull_and_push_the_snapshot_data(
            LOCKDOWN_ENDPOINT, self.lockdown_table_name, hashed_events_list, HASH_FIELD_LIST
        )
