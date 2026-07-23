"""Module for constants."""

import os

# Armis constants
API_KEY = os.environ.get("ArmisSecretKey", "")
URL = os.environ.get("ArmisURL", "")
ACCESS_TOKEN_SUFFIX = "/access_token/"
SEARCH_SUFFIX = "/search/"
ACTIVITY_FIELDS = ["title", "type", "time", "site", "sensor", "protocol", "content", "activityUUID"]
ALERT_FIELDS = [
    "alertId",
    "type",
    "title",
    "description",
    "severity",
    "time",
    "status",
    "deviceIds",
    "activityUUIDs",
]
RETRY_COUNT_401 = 3
SEVERITY = os.environ.get("Severity", "Low")
SEVERITIES = ["Low", "Medium", "High", "Critical"]

# Sentinel constants
CONNECTION_STRING = os.environ.get("AzureWebJobsStorage", "")
ARMIS_ALERTS_TABLE = os.environ.get("ArmisAlertsTableName", "")
ARMIS_ACTIVITIES_TABLE = os.environ.get("ArmisActivitiesTableName", "")
WORKSPACE_ID = os.environ.get("WorkspaceID", "")
WORKSPACE_KEY = os.environ.get("WorkspaceKey", "")
KEYVAULT_NAME = os.environ.get("KeyVaultName", "")
CHUNK_SIZE = 35
FILE_SHARE = "funcstatemarkershare"
CHECKPOINT_FILE_TIME = "funcarmisalertsfile"
CHECKPOINT_FILE_OFFSET = "armisalertoffset"
LOG_FORMAT = "Armis Alerts Activities Connector: (method = {}) : {}"
REQUEST_TIMEOUT = 300
CHECKPOINT_TABLE_NAME = "ArmisAlertActivityCheckpoint"
FUNCTION_APP_TIMEOUT_SECONDS = 570

DCR_RULE_ID = os.environ.get("DCR_RULE_ID")
AZURE_DATA_COLLECTION_ENDPOINT = os.environ.get("AZURE_DATA_COLLECTION_ENDPOINT")
SCOPE = os.environ.get("SCOPE")
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
