"""
A module to manage state persistence using Azure File Share.

"""

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient

class StateManager:
    """
    A class to manage state persistence using Azure File Share.

    This class provides methods to store and retrieve a marker in an Azure File Share,
    ensuring that the state is maintained across function executions.

    Attributes:
        share_cli (ShareClient): Client to interact with the Azure File Share.
        file_cli (ShareFileClient): Client to interact with the specific state marker file.

    Methods:
        post(marker_text: str):
            Uploads a state marker to the file. If the share does not exist, it creates one first.

        get() -> str | None:
            Retrieves the stored state marker from the file. Returns None if the
             file does not exist.
    """

    def __init__(
        self,
        connection_string: str,
        share_name: str = "funcstatemarkershare",
        file_path: str = "funcstatemarkerfile",
    ):
        """
        Initializes the StateManager with the Azure File Share connection.

        Args:
            connection_string (str): Azure Storage connection string.
            share_name (str, optional): Name of the Azure File Share.
              Defaults to "funcstatemarkershare".
            file_path (str, optional): Path to the state marker file.
              Defaults to "funcstatemarkerfile".
        """
        self.share_cli = ShareClient.from_connection_string(
            conn_str=connection_string, share_name=share_name, is_emulated=True
        )
        self.file_cli = ShareFileClient.from_connection_string(
            conn_str=connection_string,
            share_name=share_name,
            file_path=file_path,
            is_emulated=True,
        )

    def post(self, marker_text: str):
        """
        Stores a marker in the Azure File Share. If the share does not exist, it creates one.

        Args:
            marker_text (str): The text to be stored as a state marker.
        """
        try:
            self.file_cli.upload_file(marker_text)
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)

    def get(self) -> str | None:
        """
        Retrieves the stored state marker.

        Returns:
            str | None: The state marker text if found, otherwise None.
        """
        try:
            return self.file_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            return None
