"""This file contains constants require for Team Cymru Scout Data Connector."""

import os

# Environment Variables
WORKSPACE_ID = os.environ.get("WorkspaceID")
WORKSPACE_KEY = os.environ.get("WorkspaceKey")
DETECTIONS_TABLE_NAME = os.environ.get("DetectionsTableName")
LOG_LEVEL = os.environ.get("LogLevel")

DEFAULT_LOG_LEVEL = "INFO"
LOGS_STARTS_WITH = "ExtraHop:"
INGESTION_ERROR_SLEEP_TIME = 30
SENTINEL_RETRY_COUNT = 5
MAX_TIMEOUT_SENTINEL = 180

DCR_RULE_ID = os.environ.get("DCR_RULE_ID")
AZURE_DATA_COLLECTION_ENDPOINT = os.environ.get("AZURE_DATA_COLLECTION_ENDPOINT")
SCOPE = os.environ.get("SCOPE")
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
