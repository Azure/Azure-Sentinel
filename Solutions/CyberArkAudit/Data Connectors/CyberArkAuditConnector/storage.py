import json
import logging
import os

from azure.storage.blob import ContainerClient


class BaseStorage:
    def save(self, data: dict, file_name: str) -> None:
        pass

    def load(self, file_name: str) -> dict:
        pass


class LocalStorage(BaseStorage):
    def save(self, data: dict, file_name: str) -> None:
        with open(file_name, 'w+') as file:
            json.dump(data, file)

    def load(self, file_name: str) -> dict:
        if os.path.exists(file_name):
            with open(file_name, 'r') as file:
                return json.load(file)
        return {}


class AzureBlobStorage(BaseStorage):
    def __init__(self):
        storage_account = os.environ.get('AzureWebJobsStorage')
        audit_container = os.environ.get('StorageContainer', 'audit-query-storage')
        self.container_client = ContainerClient.from_connection_string(conn_str=storage_account,
                                                                       container_name=audit_container)

    def save(self, data: dict, file_name: str) -> None:
        blob_client = self.container_client.get_blob_client(blob=file_name)

        try:
            blob_client.upload_blob(json.dumps(data), overwrite=True)
            logging.info(f'Blob {file_name} successfully written')
        except Exception as e:
            logging.error(f'Error writing to blob {file_name}: {str(e)}')

    def load(self, file_name: str) -> dict:
        blob_client = self.container_client.get_blob_client(blob=file_name)
        try:
            blob_data = blob_client.download_blob().readall()
            return json.loads(blob_data)
        except Exception as e:
            logging.error(f'Error reading blob {file_name}: {str(e)}')
            return {}
