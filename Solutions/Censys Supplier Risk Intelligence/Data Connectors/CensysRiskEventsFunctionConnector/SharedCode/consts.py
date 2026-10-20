"""Constants and configuration read from the Function App settings."""
import os

API_BASE_URL = "https://api.platform.censys.io"
RISK_EVENTS_PATH = "/v1/supplychains/default/risk-events"
PAGE_SIZE = 1000
REQUEST_TIMEOUT = 60
MAX_RETRIES = 5
DEFAULT_START_TIME = "1970-01-01T00:00:00Z"
RETENTION_DAYS = 29
# No Censys API call starts after MAX_RUN_SECONDS, and no call may run past HARD_LIMIT_SECONDS, so the run always ends
# before the 10 minute function timeout. Progress is checkpointed after every page.
MAX_RUN_SECONDS = 540
HARD_LIMIT_SECONDS = 580

API_TOKEN = os.environ.get("CensysApiToken")
ORGANIZATION_ID = os.environ.get("OrganizationId")
INITIAL_START_TIME = os.environ.get("InitialStartTime", "")
SUPPLIER_IDS = os.environ.get("SupplierIds", "")
RISK_TYPE_IDS = os.environ.get("RiskTypeIds", "")
CHANGE_TYPES = os.environ.get("ChangeTypes", "")
SEVERITY = os.environ.get("Severity", "")
RAPID_RESPONSE = os.environ.get("RapidResponse", "")

ALLOWED_CHANGE_TYPES = ("opened", "resolved", "reopened")
ALLOWED_SEVERITIES = ("LOW", "MEDIUM", "HIGH", "CRITICAL")

CONN_STRING = os.environ.get("AzureWebJobsStorage")
CHECKPOINT_TABLE_NAME = os.environ.get("CheckpointTableName", "CensysSRIRiskEventsCheckpoint")
CHECKPOINT_PARTITION_KEY = "CensysSRIRiskEvents"

DATA_COLLECTION_ENDPOINT = os.environ.get("AZURE_DATA_COLLECTION_ENDPOINT")
DATA_COLLECTION_RULE_ID = os.environ.get("AZURE_DATA_COLLECTION_RULE_ID")
STREAM_NAME = os.environ.get("StreamName", "Custom-CensysRiskEvents_CL")
SCOPE = os.environ.get("SCOPE", "https://monitor.azure.com/.default")

# Top-level event fields declared in the data collection rule stream
EVENT_FIELDS = ("id", "inserted_at", "occurred_at", "change_type", "risk_instance")
LOG_PREFIX = "CensysSRI"
