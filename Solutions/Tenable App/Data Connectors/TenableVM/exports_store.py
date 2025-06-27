import logging

from enum import Enum
from azure.data.tables import TableClient, UpdateMode, TableServiceClient
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    HttpResponseError,
)
from .tenable_helper import TenableStatus

logs_starts_with = "TenableVM"
function_name = "exports_store"


class ExportsTableStore:

    def __init__(self, connection_string, table_name):
        """
        Initializes a new instance of the ExportsTableStore class.

        :param connection_string: The storage connection string
        :type connection_string: str
        :param table_name: The name of the table
        :type table_name: str
        """
        self.connection_string = connection_string
        self.table_name = table_name

    def create(self):
        """
        Creates the table if it does not exist.
        """
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                table_client.create_table()
            except ResourceExistsError:
                logging.warning(f"{logs_starts_with} {function_name}: Table already exists")

    def post(self, pk: str, rk: str, data: dict = None):
        """
        Posts a new entity to the table.

        :param pk: The partition key for the entity
        :type pk: str
        :param rk: The row key for the entity
        :type rk: str
        :param data: The data for the entity
        :type data: dict
        """
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            entity_template = {
                "PartitionKey": pk,
                "RowKey": rk,
            }
            if data is not None:
                entity_template.update(data)
            try:
                table_client.create_entity(entity_template)
            except Exception as e:
                logging.warning(f"{logs_starts_with} {function_name}: Could not post entity to table")
                logging.warning(f"{logs_starts_with} {function_name}: {e}")
                raise e

    def get(self, pk: str, rk: str):
        """
        Retrieves an entity from the table by its partition and row keys.

        :param pk: The partition key for the entity
        :type pk: str
        :param rk: The row key for the entity
        :type rk: str
        :return: The entity if it exists, None otherwise
        :rtype: dict
        """
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                logging.info(f"{logs_starts_with} {function_name}: Looking for {pk} - {rk} on table {self.table_name}")
                return table_client.get_entity(pk, rk)
            except ResourceNotFoundError:
                return None

    def upsert(self, pk: str, rk: str, data: dict = None):
        """
        Upserts an entity into the table. If the entity already exists, it is
        updated. If not, it is created.

        :param pk: The partition key for the entity
        :type pk: str
        :param rk: The row key for the entity
        :type rk: str
        :param data: The data for the entity
        :type data: dict
        :return: The updated or created entity
        :rtype: dict
        """
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            logging.info(f"{logs_starts_with} {function_name}: Upserting {pk} - {rk} on table {self.table_name}")
            entity_template = {
                "PartitionKey": pk,
                "RowKey": rk,
            }
            if data is not None:
                entity_template.update(data)
            return table_client.upsert_entity(mode=UpdateMode.REPLACE, entity=entity_template)

    def update_if_found(self, pk: str, rk: str, data: dict = None):
        """
        Updates an entity in the table if it already exists. If the entity does
        not exist, nothing is done.

        :param pk: The partition key for the entity
        :type pk: str
        :param rk: The row key for the entity
        :type rk: str
        :param data: The data to update the entity with
        :type data: dict
        """
        if self.get(pk, rk) is not None:
            self.merge(pk, rk, data)

    def query_by_partition_key(self, pk):
        """
        Queries the table for entities with a specific partition key.

        :param pk: The partition key to query for
        :type pk: str
        :return: A list of entities with the given partition key
        :rtype: list
        """
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        parameters = {"key": pk}
        name_filter = "PartitionKey eq @key"
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_finished_chunks_by_partition_key(self, pk):
        """
        Queries the table for entities with a specific partition key and
        jobStatus equal to "finished".

        :param pk: The partition key to query for
        :type pk: str
        :return: A list of entities with the given partition key and jobStatus
        :rtype: list
        """
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        parameters = {"key": pk, "status": TenableStatus.finished.value}
        name_filter = "PartitionKey eq @key and jobStatus eq @status"
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_all_finished_chunks(self):
        """
        Queries the table for entities with jobStatus equal to "finished".

        :return: A list of entities with the given jobStatus
        :rtype: list
        """
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        parameters = {"status": TenableStatus.finished.value}
        name_filter = "jobStatus eq @status"
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_all_queued_finished_and_expired_chunks(self):
        """
        Queries the table for entities with jobStatus equal to "finished" or "queued".

        :return: A list of entities with the given jobStatus
        :rtype: list
        """
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        parameters = {
            "finishedStatus": TenableStatus.finished.value,
            "queuedStatus": TenableStatus.queued.value,
            "expiredStatus": TenableStatus.expired.value
        }
        name_filter = "jobStatus eq @queuedStatus or jobStatus eq @finishedStatus or jobStatus eq @expiredStatus"
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_failed_chunks_by_partition_key(self, pk):
        """
        Queries the table for entities with a specific partition key and
        jobStatus equal to "failed".

        :param pk: The partition key to query for
        :type pk: str
        :return: A list of entities with the given partition key and jobStatus
        :rtype: list
        """
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        parameters = {"key": pk, "status": TenableStatus.failed.value}
        name_filter = "PartitionKey eq @key and jobStatus eq @status"
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_all_failed_chunks(self):
        """
        Queries the table for entities with jobStatus equal to "failed".

        :return: A list of entities with the given jobStatus
        :rtype: list
        """
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        parameters = {"status": TenableStatus.failed.value}
        name_filter = "jobStatus eq @status"
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_all_queued_chunks(self):
        """
        Queries the table for entities with jobStatus equal to "queued".

        :return: A list of entities with the given jobStatus
        :rtype: list
        """
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        parameters = {"status": TenableStatus.queued.value}
        name_filter = "jobStatus eq @status"
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_all_processing_chunks(self):
        """
        Queries the table for entities with jobStatus equal to "processing", "failed" or "queued".

        :return: A list of entities with the given jobStatus
        :rtype: list
        """
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        parameters = {
            "failedStatus": TenableStatus.failed.value,
            "queuedStatus": TenableStatus.queued.value,
        }
        name_filter = "jobStatus eq @failedStatus or jobStatus eq @queuedStatus"
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def batch(self, operations):
        """
        Submits a batch of operations to the table as a transaction.

        :param operations: A list of operations to submit
        :type operations: list
        :return: A list of the results of the operations
        :rtype: list
        """
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            return table_client.submit_transaction(operations=operations)

    def list_all(self):
        """
        Lists all entities in the table.

        :return: A list of entities in the table
        :rtype: list
        """
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        return table_client.list_entities()

    def merge(self, pk: str, rk: str, data: dict = None):
        """
        Merges an entity into the table. If the entity already exists, its
        values are updated. If not, it is created.

        :param pk: The partition key for the entity
        :type pk: str
        :param rk: The row key for the entity
        :type rk: str
        :param data: The data for the entity
        :type data: dict
        :return: The updated or created entity
        :rtype: dict
        """
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            logging.info(f"{logs_starts_with} {function_name}: Upserting {pk} - {rk} on table {self.table_name}")
            entity_template = {
                "PartitionKey": pk,
                "RowKey": rk,
            }
            if data is not None:
                entity_template.update(data)
            return table_client.upsert_entity(mode=UpdateMode.MERGE, entity=entity_template)


def list_tables_in_storage_account(conn_str):
    """
    Lists all tables in a given storage account.

    :param conn_str: The connection string for the storage account
    :type conn_str: str
    :return: A list of TableItem objects, each representing a table in the storage account
    :rtype: list
    """
    service = TableServiceClient.from_connection_string(conn_str)
    tables = service.list_tables()
    return tables


def update_chunk_status_in_batch(chunks_to_be_updated: dict, table_client: ExportsTableStore) -> None:
    """Updates the status of chunks in the table in batches.

    Args:
        chunks_to_be_updated (dict): A dictionary with job_id as key and a list of tuples containing the action, data and options as values.
            The tuple is in the format of (action, data, options).
            The action is operation to perform, data is the data to be updated
            and options is a dictionary with other arguments if required.
    """
    batch_size = 50
    for job in chunks_to_be_updated.keys():
        batches = [
            chunks_to_be_updated[job][i: i + batch_size]
            for i in range(0, len(chunks_to_be_updated[job]), batch_size)
        ]
        try:
            for batch in batches:
                logging.debug(f"{logs_starts_with} {function_name}: Updating data in batch for job_id: {job}")
                table_client.batch(batch)
        except Exception as e:
            logging.error(f"{logs_starts_with} {function_name}: Error in updating chunk status in batch: {e}")


def update_chunk_status_for_old_jobs(table_client: ExportsTableStore) -> None:
    """This function updates the status of chunks in the table to EXPIRED if they are queued but the job has not been polled in a while.
    It is used to prevent the chunk from remaining in the queue indefinitely if the job is not polled.
    """
    chunks_to_be_updated = {}
    logging.info(f"{logs_starts_with} {function_name}: Updating chunk status to EXPIRED for old jobs.")
    queued_chunks = table_client.query_for_all_queued_chunks()
    queued_chunks_list = list(queued_chunks)
    for chunk in queued_chunks_list:
        job_id = chunk.get("PartitionKey")
        chunk_id = chunk.get("RowKey")
        if job_id not in chunks_to_be_updated:
            chunks_to_be_updated[job_id] = [("upsert", {"PartitionKey": job_id, "RowKey": chunk_id,
                                             "jobStatus": TenableStatus.expired.value}, {"mode": "merge"})]
        else:
            chunks_to_be_updated[job_id].append(
                ("upsert", {"PartitionKey": job_id, "RowKey": chunk_id, "jobStatus": TenableStatus.expired.value}, {"mode": "merge"}))

    update_chunk_status_in_batch(chunks_to_be_updated, table_client)


class ExportsTableNames(Enum):
    TenableExportStatsTable = "TenableExportStatsTable"
    TenableAssetExportTable = "TenableAssetExportTable"
    TenableVulnExportTable = "TenableVulnExportTable"
    TenableComplianceExportTable = "TenableComplianceExportTable"
    TenableExportCheckpointTable = "TenableExportCheckpointTable"
    TenableWASAssetExportTable = "TenableWASAssetExportTable"
    TenableWASVulnExportTable = "TenableWASVulnExportTable"
