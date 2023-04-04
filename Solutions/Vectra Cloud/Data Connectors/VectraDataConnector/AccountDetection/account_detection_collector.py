"""This account_detection_collector file will pull and push the data of account detection."""
from ..SharedCode.collector import BaseCollector
from ..SharedCode.state_manager import StateManager
from ..SharedCode.consts import ACCOUNT_DETECTION_TABLE_NAME

ACCOUNT_DETECTION_ENDPOINT = "/api/v3.2/events/account_detection"
MODIFIED_FIELDS = ["detail"]


class AccountDetectionCollector(BaseCollector):
    """This class contains methods to create object and call get checkpoint and 'pull and push the data'method."""

    def __init__(self, applogger, function_name) -> None:
        """Initialize instance variable for class."""
        super(AccountDetectionCollector, self).__init__(applogger, function_name)
        self.account_detection_table_name = ACCOUNT_DETECTION_TABLE_NAME
        self.state = StateManager(connection_string=self.connection_string, file_path="account_detection")

    def get_account_detection_data_and_ingest_into_sentinel(self):
        """To call get checkpoint and 'pull and push the data' method."""
        field, checkpoint = self.get_checkpoint_field_and_value()
        self.pull_and_push_the_data(
            ACCOUNT_DETECTION_ENDPOINT, field, checkpoint, self.account_detection_table_name, fields=MODIFIED_FIELDS
        )
