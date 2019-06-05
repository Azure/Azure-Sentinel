from datetime import *
import time
import azure.mgmt.storage.models
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlockBlobService, PageBlobService, AppendBlobService
from azure.storage.blob.models import BlobBlock, ContainerPermissions, ContentSettings

class StorageHelper:
    def __init__(self, storage_client):
        self.storage_client = storage_client

    def is_storage_account_name_available(self, storage_account_name):
        return self.storage_client.storage_accounts.check_name_availability(storage_account_name)

    def create_storage_account_async(self, storage_account_name, resource_group, **kwargs):
        storage_params = azure.mgmt.storage.models.StorageAccountCreateParameters(
            sku=azure.mgmt.storage.models.Sku(name='standard_lrs'),
            kind=azure.mgmt.storage.models.Kind.storage,
            location=kwargs['storage_location']
        )
        async_storage_creation = self.storage_client.storage_accounts.create(
            resource_group,
            storage_account_name,
            storage_params
        )
        storage_account = async_storage_creation.result()    

    def get_storage_account_names(self, resource_group):
        storage_account_list = self.storage_client.storage_accounts.list_by_resource_group(resource_group)
        return [item.name for item in storage_account_list]

    def get_storage_account_properties(self, storage_account_name, resource_group):
        return self.storage_client.storage_accounts.get_properties(resource_group, storage_account_name)

    def get_storage_account_key(self, storage_account_name, resource_group):
        storage_keys = self.storage_client.storage_accounts.list_keys(resource_group, storage_account_name)
        if storage_keys is not None:
            return {v.key_name: v.value for v in storage_keys.keys}['key1']
        else:
            return None

    def initialize_block_blob_service(self, storage_account_name, storage_key, blob_container_name):
        self.storage_account_name = storage_account_name
        self.storage_key = storage_key
        self.blob_container_name = blob_container_name

        self.block_blob_service = BlockBlobService(account_name=self.storage_account_name, account_key=self.storage_key) 

    def create_blob_container(self):
        return self.block_blob_service.create_container(self.blob_container_name) 

    def get_blob_container(self):
        containers = self.block_blob_service.list_containers(self.blob_container_name)
        return next(c for c in containers if c.name == self.blob_container_name)

    def copy_vhd(self, file_name, file_path):
        status = self.block_blob_service.copy_blob(self.blob_container_name, file_name, file_path)
        if status.status == 'pending':
            time.sleep(120)

    def generate_blob_container_sas_url(self, expiration_in_days):
        container_permission = ContainerPermissions(read=True, write=True, list=True)
        return self.block_blob_service.generate_container_shared_access_signature(container_name = self.blob_container_name, permission=container_permission, protocol='https', start=datetime.now(), expiry=datetime.now() + timedelta(days=expiration_in_days))

    def build_upload_container_path(self, target_os_type, sas_url):
        return 'https://{0}.blob.core.windows.net/{1}/{2}/{3}?{4}'.format(self.storage_account_name, self.blob_container_name, target_os_type.lower(), 'piresults.json', sas_url)

    def get_container_name_list(self, resource_group, storage_account_name, blob_container_name):
        key = self.get_storage_account_key(storage_account_name, resource_group)
        self.initialize_block_blob_service(storage_account_name, key, blob_container_name)
        containers = self.block_blob_service.list_containers()
        return list(c.name for c in containers)

# end of the class
