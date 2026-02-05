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
