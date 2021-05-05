import json
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import os
import logging


class AzureSecretHandler:

    def __init__(self, KVUri):
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=KVUri, credential=credential)

    def get_secret(self, key):
        return self.client.get_secret(key)

    def set_secret(self, key, value):
        self.client.set_secret(key, value)
    
    # def delete_secret(self, key):

    
    # def update_secret(self, key, value):