"""This file contains implementation of companies endpoint."""

from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableServiceClient, UpdateMode

from ..SharedCode.logger import applogger
from ..SharedCode.bitsight_exception import BitSightException


class CheckpointManager:
    """Class for managing checkpoints and state information."""

    def __init__(self, connection_string: str, table_name: str):
        """
        Initializes CheckpointManager object.

        Args:
            connection_string (str): Storage account connection string.
            table_name (str): Name of the table to be used for checkpointing.
        """
        self.connection_string = connection_string
        self.table_name = table_name
        self.service_client = TableServiceClient.from_connection_string(conn_str=self.connection_string)
        self.table_client = self._get_or_create_table()

    def _get_or_create_table(self) -> TableServiceClient:
        """
        Gets or creates a table client for the given table name.

        Returns:
            TableServiceClient: Table client for the given table name.

        Raises:
            BitSightException: Raised if there is an error creating or accessing the table.
        """
        try:
            applogger.debug(f"Accessing table : {self.table_name}")
            table_client = self.service_client.create_table_if_not_exists(self.table_name)
            return table_client
        except Exception as e:
            applogger.error(f"Error creating or accessing table {self.table_name} : {e}")
            raise BitSightException(f"Error creating or accessing table {self.table_name} : {e}")

    def get_checkpoint(self, partition_key: str, row_key: str) -> str:
        """
        Gets the checkpoint value for the given partition key and row key.

        Args:
            partition_key (str): Partition key.
            row_key (str): Row key.

        Returns:
            str: Checkpoint value.

        Raises:
            BitSightException: Raised if there is an error getting the checkpoint.
        """
        try:
            applogger.debug("Getting checkpoint")
            entity = self.table_client.get_entity(partition_key=partition_key, row_key=row_key)
            return entity.get("Value")
        except ResourceNotFoundError:
            applogger.warning("Checkpoint not found")
            return None
        except Exception as e:
            applogger.error(f"Error getting checkpoint: {e}")
            raise BitSightException(f"Error getting checkpoint: {e}")

    def set_checkpoint(self, partition_key: str, row_key: str, value: str) -> None:
        """
        Sets the checkpoint for a given partition key and row key.

        Args:
            partition_key (str): Partition key.
            row_key (str): Row key.
            value (str): Value to be set as the checkpoint.

        Raises:
            BitSightException: Raised if there is an error setting the checkpoint.
        """
        applogger.debug(f"Setting checkpoint to {value}")
        entity = {"PartitionKey": partition_key, "RowKey": row_key, "Value": value}
        try:
            self.table_client.upsert_entity(mode=UpdateMode.MERGE, entity=entity)
        except Exception as e:
            applogger.error(f"Error setting checkpoint: {e}")
            raise BitSightException(f"Error setting checkpoint: {e}")
