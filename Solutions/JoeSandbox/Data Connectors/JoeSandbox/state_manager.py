"""
StateManager of Azure Function App
"""

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.fileshare import ShareClient, ShareFileClient


class StateManager:
    """
    Manages state persistence using Azure File Share storage.

    Parameters
    ----------
    connection_string : str
        Azure Storage account connection string.
    share_name : str, optional
        Name of the Azure File Share to use (default is "funcstatemarkershare").
    file_path : str, optional
        Path of the file within the share to store the marker (default is "funcstatemarkerfile").
    """

    def __init__(
        self,
        connection_string: str,
        share_name="funcstatemarkershare",
        file_path="funcstatemarkerfile",
    ):
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
        Saves the given marker text to the Azure File Share.

        Parameters
        ----------
        marker_text : str
            The content (typically a timestamp) to store in the state file.
        """
        try:
            self.file_cli.upload_file(marker_text)
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)

    def get(self):
        """
        Retrieves the stored marker text from the Azure File Share.

        Returns
        -------
        str or None
            The stored marker text.
        """
        try:
            return self.file_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            return None
