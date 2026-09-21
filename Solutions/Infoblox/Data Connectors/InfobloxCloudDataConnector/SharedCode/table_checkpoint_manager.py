"""Azure Table Storage wrapper and table-based checkpoint manager."""

import logging
from azure.data.tables import TableClient, UpdateMode
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError, HttpResponseError


class ExportsTableStore:
    """Thin wrapper around azure.data.tables.TableClient for checkpoint storage."""

    # Process-level cache of table names already ensured to exist, so create()
    # skips the network round-trip on subsequent instantiations in a warm process.
    _created_tables = set()

    def __init__(self, connection_string, table_name):
        """Initialize ExportsTableStore object."""
        self.connection_string = connection_string
        self.table_name = table_name

    def create(self):
        """Create the backing table if it does not already exist."""
        if self.table_name in ExportsTableStore._created_tables:
            return
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                table_client.create_table()
                logging.info("Checkpoint Table created")
            except ResourceExistsError:
                logging.warning("Table already exists")
        ExportsTableStore._created_tables.add(self.table_name)

    def post(self, pk: str, rk: str, data: dict = None):
        """Create a new entity, raising if one already exists for pk/rk."""
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            entity_template = {
                "PartitionKey": pk,
                "RowKey": rk,
            }
            if data is not None:
                entity_template.update(data)
            try:
                table_client.create_entity(entity_template)
            except Exception:
                logging.exception("could not post entity to table")
                raise

    def get(self, pk: str, rk: str):
        """Get the entity for pk/rk, or None if it does not exist."""
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                logging.info("looking for {} - {} on table {}".format(pk, rk, self.table_name))
                return table_client.get_entity(pk, rk)
            except ResourceNotFoundError:
                return None

    def upsert(self, pk: str, rk: str, data: dict = None):
        """Replace the entity for pk/rk with data, creating it if needed."""
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            logging.info("upserting {} - {} on table {}".format(pk, rk, self.table_name))
            entity_template = {
                "PartitionKey": pk,
                "RowKey": rk,
            }
            if data is not None:
                entity_template.update(data)
            return table_client.upsert_entity(mode=UpdateMode.REPLACE, entity=entity_template)

    def update_if_found(self, pk: str, rk: str, data: dict = None):
        """Merge data into the entity for pk/rk only if it already exists."""
        if self.get(pk, rk) is not None:
            self.merge(pk, rk, data)

    def query_by_partition_key(self, pk):
        """Return all entities for the given partition key."""
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            parameters = {u"key": pk}
            name_filter = u"PartitionKey eq @key"
            try:
                # Materialize inside the context manager; query_entities is lazy and
                # would fail if iterated after the client is closed.
                return list(table_client.query_entities(name_filter, parameters=parameters))
            except HttpResponseError as e:
                logging.error("Failed to query entities by partition key {}: {}".format(pk, str(e)))
                return []

    def batch(self, operations):
        """Submit a batch of table operations as a single transaction."""
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            return table_client.submit_transaction(operations=operations)

    def list_all(self):
        """Return all entities in the table."""
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        return table_client.list_entities()

    def merge(self, pk: str, rk: str, data: dict = None):
        """Merge data into the entity for pk/rk, creating it if needed."""
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            logging.info("upserting {} - {} on table {}".format(pk, rk, self.table_name))
            entity_template = {
                "PartitionKey": pk,
                "RowKey": rk,
            }
            if data is not None:
                entity_template.update(data)
            return table_client.upsert_entity(mode=UpdateMode.MERGE, entity=entity_template)

    def delete(self, pk: str, rk: str):
        """Delete the entity for pk/rk. No-op if not found."""
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                table_client.delete_entity(pk, rk)
                logging.info("Deleted entity {} - {} from table {}".format(pk, rk, self.table_name))
            except ResourceNotFoundError:
                logging.warning("Entity {} - {} not found in table {}, skipping delete".format(pk, rk, self.table_name))


class TableCheckpointManager:
    """Adapter over ExportsTableStore for time-based checkpoints.

    Provides a StateManager-compatible post(str) / get() -> str interface.

    Args:
        connection_string (str): Azure Storage connection string.
        row_key (str): Unique checkpoint key (equivalent to file_path in StateManager).
        table_name (str): Azure Table name to store checkpoints.
    """

    PARTITION_KEY = "Infoblox"

    def __init__(self, connection_string: str, row_key: str, table_name: str):
        """Initialize TableCheckpointManager object."""
        self.row_key = row_key
        self._store = ExportsTableStore(connection_string, table_name)
        self._store.create()

    def post(self, value: str):
        """Upsert checkpoint value to Azure Table."""
        self._store.upsert(self.PARTITION_KEY, self.row_key, {"value": value})

    def get(self):
        """Get checkpoint value from Azure Table. Returns None if not found."""
        entity = self._store.get(self.PARTITION_KEY, self.row_key)
        if entity is None:
            return None
        return entity.get("value")

    def delete(self):
        """Delete checkpoint entry from Azure Table. No-op if not found."""
        self._store.delete(self.PARTITION_KEY, self.row_key)
