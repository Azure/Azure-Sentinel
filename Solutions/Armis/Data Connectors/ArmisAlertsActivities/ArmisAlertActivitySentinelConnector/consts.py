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

# Sentinel constants
CONNECTION_STRING = os.environ.get("AzureWebJobsStorage", "")
ARMIS_ALERTS_TABLE = os.environ.get("ArmisAlertsTableName", "")
ARMIS_ACTIVITIES_TABLE = os.environ.get("ArmisActivitiesTableName", "")
WORKSPACE_ID = os.environ.get("WorkspaceID", "")
WORKSPACE_KEY = os.environ.get("WorkspaceKey", "")
CHUNK_SIZE = 35
FILE_SHARE = "funcstatemarkershare"
CHECKPOINT_FILE_TIME = "funcarmisalertsfile"
CHECKPOINT_FILE_OFFSET = "armisalertoffset"
LOG_FORMAT = "Armis Alerts Activities Connector: (method = {}) : {}"
REQUEST_TIMEOUT = 300
CHECKPOINT_TABLE_NAME = "ArmisAlertActivityCheckpoint"
