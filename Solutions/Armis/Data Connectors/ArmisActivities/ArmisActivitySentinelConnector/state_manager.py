"""This module will help to save file to statemanager."""
from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient
from azure.core.exceptions import ResourceNotFoundError


class StateManager:
    """State manager class for specific operation."""

    def __init__(
        self,
        connection_string,
        file_path,
        share_name="funcstatemarkershare",
    ):
        """Initialize the share_cli and file_client."""
        self.share_cli = ShareClient.from_connection_string(
            conn_str=connection_string, share_name=share_name
        )
        self.file_cli = ShareFileClient.from_connection_string(
            conn_str=connection_string, share_name=share_name, file_path=file_path
        )

    def post(self, marker_text: str):
        """Post method for posting the data to azure storage."""
        try:
            self.file_cli.upload_file(marker_text)
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)

    def get(self):
        """Get method for getting the data from azure storage."""
        try:
            return self.file_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            return None
