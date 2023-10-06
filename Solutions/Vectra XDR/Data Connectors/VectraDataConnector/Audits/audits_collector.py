"""This audits_collector file will pull and push the data of audits."""
from ..SharedCode.collector import BaseCollector
from ..SharedCode.state_manager import StateManager
from ..SharedCode.consts import AUDITS_TABLE_NAME

AUDIT_ENDPOINT = "/api/v3.3/events/audits"
MODIFIED_FIELDS = ["event_data"]


class AuditsCollector(BaseCollector):
    """This class contains methods to create object and call get checkpoint and 'pull and push the data'method."""

    def __init__(self, applogger, function_name, client_id, client_secret) -> None:
        """Initialize instance variable for class."""
        super(AuditsCollector, self).__init__(applogger, function_name, client_id, client_secret)
        self.audits_table_name = AUDITS_TABLE_NAME
        self.state = StateManager(connection_string=self.connection_string, file_path="audits")

    def get_audit_data_and_ingest_into_sentinel(self):
        """To call get checkpoint and 'pull and push the data' method."""
        field, checkpoint = self.get_checkpoint_field_and_value()
        self.pull_and_push_the_data(AUDIT_ENDPOINT, field, checkpoint, self.audits_table_name, fields=MODIFIED_FIELDS)
