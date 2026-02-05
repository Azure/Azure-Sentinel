"""This module will help to save file to state manager."""

from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError


class StateManager:
    """State manager class for specific operation.

    This class will help to manage the state of the operation
    by saving and getting data from Azure Storage.

    Args:
        connection_string (str): Azure Storage connection string.
        file_path (str): File path on the share.
        share_name (str): Name of the share.
    """

    def __init__(self, connection_string, file_path, share_name):
        """Initialize the share_cli and file_cli."""
        self.share_cli = ShareClient.from_connection_string(
            conn_str=connection_string, share_name=share_name
        )
        self.file_cli = ShareFileClient.from_connection_string(
            conn_str=connection_string, share_name=share_name, file_path=file_path
        )

    def post(self, marker_text: str):
        """Post method for posting the data to Azure Storage.

        This method will upload the given text to the
        Azure Storage as a file.

        Args:
            marker_text (str): String to be saved in the file.
        """
        try:
            self.file_cli.upload_file(marker_text)
        except ResourceNotFoundError:
            try:
                self.share_cli.create_share()
                self.file_cli.upload_file(marker_text)
            except ResourceExistsError:
                self.file_cli.upload_file(marker_text)

    def get(self):
        """Get method for getting the data from Azure Storage.

        This method will download the file from Azure Storage
        and return the contents as a string.

        Returns:
            str: The contents of the file.
        """
        try:
            return self.file_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            return None

    def delete(self):
        """Delete method for deleting the data from Azure Storage.

        This method will delete the file from Azure Storage.
        """
        try:
            self.file_cli.delete_file()
        except ResourceNotFoundError:
            raise ResourceNotFoundError("File not found to be deleted.")
