"""Module for constants."""

import os

API_KEY = os.environ.get("ArmisSecretKey")
URL = os.environ.get("ArmisURL")
CONN_STRING = os.environ.get("AzureWebJobsStorage")
ARMIS_DEVICES_TABLE = os.environ.get("ArmisDeviceTableName")
CHECKPOINT_TABLE_NAME = "ArmisDeviceCheckpoint"
MAX_RETRY = 5
FUNCTION_APP_TIMEOUT_SECONDS = 570
KEYVAULT_NAME = os.environ.get("KeyVaultName", "")
LOG_FORMAT = "Armis Device Connector: (method = {}) : {}"

DCR_RULE_ID = os.environ.get("DCR_RULE_ID")
AZURE_DATA_COLLECTION_ENDPOINT = os.environ.get("AZURE_DATA_COLLECTION_ENDPOINT")
SCOPE = os.environ.get("SCOPE")
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
