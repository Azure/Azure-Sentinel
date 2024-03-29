import logging
from datetime import datetime, timedelta, timezone

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.data.tables import UpdateMode

log = logging.getLogger(__name__)


class StorageTableClient:
    def __init__(self, table_client):
        self._table_client = table_client
        self._partition_key = "WithSecureConnectorViaAPI"
        self._row_key = "LastSuccessfulRead"

    def get_start_timestamp(self):
        last_timestamp = self._get_timestamp()
        if last_timestamp is None:
            last_minute_timestamp = datetime.now(timezone.utc) - timedelta(minutes=1)
            last_timestamp = last_minute_timestamp.isoformat(
                sep="T", timespec="milliseconds"
            ).replace("+00:00", "Z")
            log.info(
                f"Timestamp missing from storage, generating with {last_timestamp}"
            )
            self._add_timestamp_entity(last_timestamp)
        return last_timestamp

    def save_start_timestamp(self, timestamp):
        self._update_timestamp(timestamp)

    def _add_timestamp_entity(self, timestamp):
        try:
            entity = self._timestamp_to_entity(timestamp)
            resp = self._table_client.create_entity(entity)
            log.info(f"Entity created: {resp}")
        except ResourceExistsError:
            log.info("Entity already exist")

    def _get_timestamp(self):
        try:
            return self._table_client.get_entity(self._partition_key, self._row_key)[
                self._row_key
            ]
        except ResourceNotFoundError:
            return None

    def _update_timestamp(self, timestamp):
        entity = self._timestamp_to_entity(timestamp)
        self._table_client.update_entity(entity, UpdateMode.REPLACE)

    def _timestamp_to_entity(self, timestamp):
        return {
            "PartitionKey": self._partition_key,
            "RowKey": self._row_key,
            self._row_key: timestamp,
        }
