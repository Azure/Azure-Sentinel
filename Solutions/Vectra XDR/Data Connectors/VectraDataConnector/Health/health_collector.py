"""This health_collector file will pull and push the data of health."""
from ..SharedCode.collector import BaseCollector
from ..SharedCode.state_manager import StateManager
from ..SharedCode.consts import HEALTH_TABLE_NAME, HEALTH_ENDPOINT

HASH_FIELD_LIST = []
MODIFIED_FIELDS = ["network"]

class HealthCollector(BaseCollector):
    """This class contains methods to create object and call 'pull and push the snapshot data'method."""

    def __init__(self, applogger, function_name, client_id, client_secret) -> None:
        """Initialize instance variable for class."""
        super(HealthCollector, self).__init__(applogger, function_name, client_id, client_secret)
        self.health_table_name = HEALTH_TABLE_NAME
        self.state = StateManager(
            connection_string=self.connection_string, file_path="health"
        )

    def get_health_data_and_ingest_into_sentinel(self):
        """To 'pull and push the data' method for health data."""
        self.pull_and_push_the_snapshot_data(
            HEALTH_ENDPOINT, self.health_table_name, fields=MODIFIED_FIELDS
        )
