import logging

from enum import Enum
from azure.data.tables import TableClient, UpdateMode
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError, HttpResponseError
from .tenable_helper import TenableStatus


class ExportsTableStore:

    def __init__(self, connection_string, table_name):
        self.connection_string = connection_string
        self.table_name = table_name

    def create(self):
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                table_client.create_table()
            except ResourceExistsError:
                logging.warn("Table already exists")

    def post(self, pk: str, rk: str, data: dict = None):
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            entity_template = {
                'PartitionKey': pk,
                'RowKey': rk,
            }
            if data is not None:
                entity_template.update(data)
            try:
                table_client.create_entity(entity_template)
            except Exception as e:
                logging.warn('could not post entity to table')
                logging.warn(e)
                raise e

    def get(self, pk: str, rk: str):
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                logging.info(
                    f'looking for {pk} - {rk} on table {self.table_name}')
                return table_client.get_entity(pk, rk)
            except ResourceNotFoundError:
                return None

    def upsert(self, pk: str, rk: str, data: dict = None):
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            logging.info(f'upserting {pk} - {rk} on table {self.table_name}')
            entity_template = {
                'PartitionKey': pk,
                'RowKey': rk,
            }
            if data is not None:
                entity_template.update(data)
            return table_client.upsert_entity(mode=UpdateMode.REPLACE, entity=entity_template)

    def update_if_found(self, pk: str, rk: str, data: dict = None):
        if self.get(pk, rk) is not None:
            self.merge(pk, rk, data)

    def query_by_partition_key(self, pk):
        table_client = TableClient.from_connection_string(
            self.connection_string, self.table_name)
        parameters = {u"key": pk}
        name_filter = u"PartitionKey eq @key"
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    # def get_chunk_details_by_job_id(self, pk):
    #     total_chunk_count = 0
    #     failed_chunk_count = 0
    #     finished_chunk_count = 0
    #     failed_chunk_ids = []
    #     finished_chunk_ids = []
    #     for chunk in self.query_by_partition_key(pk):
    #         total_chunk_count += 1
    #         if 'jobStatus' in chunk and chunk['jobStatus'] == 'FINISH':
    #             finished_chunk_count += 1

    #     return total_chunk_count

    def query_for_finished_chunks_by_partition_key(self, pk):
        table_client = TableClient.from_connection_string(
            self.connection_string, self.table_name)
        parameters = {'key': pk, 'status': TenableStatus.finished.value}
        name_filter = 'PartitionKey eq @key and jobStatus eq @status'
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_all_finished_chunks(self):
        table_client = TableClient.from_connection_string(
            self.connection_string, self.table_name)
        parameters = {'status': TenableStatus.finished.value}
        name_filter = 'jobStatus eq @status'
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_failed_chunks_by_partition_key(self, pk):
        table_client = TableClient.from_connection_string(
            self.connection_string, self.table_name)
        parameters = {'key': pk, 'status': TenableStatus.failed.value}
        name_filter = 'PartitionKey eq @key and jobStatus eq @status'
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_all_failed_chunks(self):
        table_client = TableClient.from_connection_string(
            self.connection_string, self.table_name)
        parameters = {'status': TenableStatus.failed.value}
        name_filter = 'jobStatus eq @status'
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def query_for_all_processing_chunks(self):
        table_client = TableClient.from_connection_string(
            self.connection_string, self.table_name)
        parameters = {
            'failedStatus': TenableStatus.failed.value,
            'processingStatus': TenableStatus.processing.value,
            'sentStatus': TenableStatus.sent_to_queue.value,
            'sendingStatus': TenableStatus.sending_to_queue.value
        }
        name_filter = 'jobStatus eq @failedStatus or jobStatus eq @processingStatus or jobStatus eq @sentStatus or jobStatus eq @sendingStatus'
        try:
            return table_client.query_entities(name_filter, parameters=parameters)
        except HttpResponseError as e:
            print(e.message)
            return []

    def batch(self, operations):
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            return table_client.submit_transaction(operations=operations)

    def list_all(self):
        table_client = TableClient.from_connection_string(
            self.connection_string, self.table_name)
        return table_client.list_entities()

    def merge(self, pk: str, rk: str, data: dict = None):
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            logging.info(f'upserting {pk} - {rk} on table {self.table_name}')
            entity_template = {
                'PartitionKey': pk,
                'RowKey': rk,
            }
            if data is not None:
                entity_template.update(data)
            return table_client.upsert_entity(mode=UpdateMode.MERGE, entity=entity_template)


class ExportsTableNames(Enum):
    TenableExportStatsTable = "TenableExportStatsTable"
    TenableAssetExportTable = "TenableAssetExportTable"
    TenableVulnExportTable = "TenableVulnExportTable"
