"""Module with constants and configurations for the Google Threat Intelligence connector."""

import os

LOG_LEVEL = os.environ.get("LogLevel", "INFO")
LOGS_STARTS_WITH = "GoogleThreatIntelligence"
LOG_FORMAT = "{}(method = {}) : {} : {}"

# *Sentinel related constants
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")
SCOPE = os.environ.get("SCOPE", "https://monitor.azure.com//.default")
KEYVAULT_NAME = os.environ.get("KEYVAULT_NAME", "")
AZURE_DATA_COLLECTION_ENDPOINT = os.environ.get("AZURE_DATA_COLLECTION_ENDPOINT", "")
DCR_RULE_ID = os.environ.get("AZURE_DATA_COLLECTION_RULE_ID", "")

# *GTI related constants
GTI_API_KEY = os.environ.get("GTI_API_KEY", "")
GTI_PROJECT_ID = os.environ.get("GTI_PROJECT_ID", "")
GTI_BASE_URL = os.environ.get("GTI_BASE_URL", "https://threatintelligence.googleapis.com")
GTI_TOKEN_EXCHANGE_URL = os.environ.get(
    "GTI_TOKEN_EXCHANGE_URL",
    "https://idp.prod.identity.proactive.virustotal.com/realms/master/exchange/api-key",
)
GTI_API_VERSION = "v1beta"
GTI_RELEVANCE_SYSTEM_ALERTS_TABLE_NAME = "RelevanceSystemAlerts"

# *Checkpoint related constants
CONN_STRING = os.environ.get("AzureWebJobsStorage", "")
FILE_SHARE_NAME = os.environ.get("File_Share_Name", "gti-connector-state")
START_DATE = os.environ.get("StartDate", "")
GTI_FILTER_EXPRESSION = os.environ.get("GTI_FILTER_EXPRESSION", "")

# *Error messages for exceptions
UNEXPECTED_ERROR_MSG = "Unexpected error : Error-{}"
CONNECTION_ERROR_MSG = "Connection error : Error-{}"
TYPE_ERROR_MSG = "Type error : Error-{}"
JSON_DECODE_ERROR_MSG = "JSONDecode error : Error-{}"
TIME_OUT_ERROR_MSG = "Timeout error : Error-{}"
MAX_RETRY_ERROR_MSG = "Max retries exceeded : {} Last exception: {}"

# *Date/time format constants
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# *Retry and timeout constants
MAX_RETRIES = 3
BACKOFF_MULTIPLIER = 2
MIN_SLEEP_TIME = 5
MAX_SLEEP_TIME = 30
MAX_TIMEOUT_SENTINEL = 120
FUNCTION_APP_TIMEOUT_SECONDS = 570

# *Data constants
PAGE_SIZE = 1000
DEFAULT_LOOKUP_DAYS = 7

# *Status code handling
RETRY_STATUS_CODE = [429, 500, 503, 502, 509]

# *Token expiry buffer in seconds (refresh token 60 seconds before expiry)
TOKEN_EXPIRY_BUFFER_SECONDS = 60
