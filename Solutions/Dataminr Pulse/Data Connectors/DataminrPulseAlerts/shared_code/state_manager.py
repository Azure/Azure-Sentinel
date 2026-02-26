"""This module will help to save file to statemanager."""
from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient
from azure.core.exceptions import ResourceNotFoundError
from ..shared_code.logger import applogger
import inspect
from ..shared_code.consts import LOGS_STARTS_WITH, MS_SHARE_NAME


class StateManager:
    """State manager class for specific operation."""

    def __init__(
        self,
        connection_string,
        file_path,
        share_name=MS_SHARE_NAME,
    ):
        """Initialize the share_cli and file_client."""
        self.share_cli = ShareClient.from_connection_string(
            conn_str=connection_string, share_name=share_name
        )
        self.file_cli = ShareFileClient.from_connection_string(
            conn_str=connection_string, share_name=share_name, file_path=file_path
        )
        self.log_starts_with = LOGS_STARTS_WITH

    def post(self, marker_text: str):
        """Post method for posting the data to azure storage."""
        try:
            self.file_cli.upload_file(marker_text)
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)

    def get(self, azure_function_name):
        """Get method for getting the data from azure storage."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            return self.file_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            applogger.info(
                "{}(method={}) : {} : last checkpoint is not available.".format(
                    self.log_starts_with, __method_name, azure_function_name
                )
            )
            return None
