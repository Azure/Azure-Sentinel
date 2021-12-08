import json
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import (
    ServiceRequestError,
    ResourceNotFoundError,
    AzureError
)
import os
import logging


class AzureSecretHandler:

    def __init__(self, KVUri):
        try:
            credential = DefaultAzureCredential()
            self.client = SecretClient(vault_url=KVUri, credential=credential)
        except ServiceRequestError as e:
            # Network error, I will let it raise to higher level
            logging.error("Azure Vault service not found %s" % str(e))
            raise
        except ResourceNotFoundError as e:
            logging.error("Azure Vault resource not found %s" % str(e))
            raise
        except AzureError as e:
            # Will catch everything that is from Azure SDK, but not the two previous
            logging.error("Azure SDK was not able to deal with my query %s" % str(e))
            raise
        except Exception as e:
            logging.error("Exception during Azure Vault Intializing %s" % str(e))
            raise

    def get_secret(self, key):
        #As per the Azure Vault rules, Key will be strictly follow the format '^[0-9a-zA-Z-]+$'
        try:
            retrived_obj = self.client.get_secret(key)
            return retrived_obj.value
        except ResourceNotFoundError as e:
            logging.info("No value found in vault for key %s" % str(key))
            return None
        except Exception as e:
            # Anything else that is not Azure related (network, stdlib, etc.), possible to raise if needed
            logging.error("Exception during get value from Azure Vault %s" % str(e))
            raise
            #return None

    def set_secret(self, key, value):
        #As per the Azure Vault rules, Key will be strictly follow the format '^[0-9a-zA-Z-]+$'.
        try:
            retrived_obj = self.client.set_secret(key, value)
            return retrived_obj.value
        except Exception as e:
            # Anything else that is not Azure related (network, stdlib, etc.)
            logging.info("Exception during creating key/value in vault  %s" % str(e))
            return None