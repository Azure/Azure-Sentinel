"""This detections_collector file will pull and push the data of detections."""
from ..SharedCode.collector import BaseCollector
from ..SharedCode.state_manager import StateManager
from ..SharedCode.consts import DETECTIONS_TABLE_NAME, DETECTIONS_ENDPOINT

MODIFIED_FIELDS = ["detail"]


class DetectionsCollector(BaseCollector):
    """This class contains methods to create object and call get checkpoint and 'pull and push the data'method."""

    def __init__(self, applogger, function_name, client_id, client_secret) -> None:
        """Initialize instance variable for class."""
        self.access_token_key = "access-token-detections"
        self.refresh_token_key = "refresh-token-detections"
        self.access_token_expiry = "expires_in_detections"
        self.refresh_token_expiry = "refresh_expires_in_detections"
        super(DetectionsCollector, self).__init__(applogger, function_name, client_id, client_secret)
        self.state = StateManager(connection_string=self.connection_string, file_path="detections")
        self.detections_table_name = DETECTIONS_TABLE_NAME

    def get_detections_data_and_ingest_into_sentinel(self):
        """To call get checkpoint and 'pull and push the data' method."""
        field, checkpoint = self.get_checkpoint_field_and_value()
        params = {"include_triaged": False}
        self.pull_and_push_the_data(
            DETECTIONS_ENDPOINT, field, checkpoint, self.detections_table_name, fields=MODIFIED_FIELDS, query_params=params
        )
