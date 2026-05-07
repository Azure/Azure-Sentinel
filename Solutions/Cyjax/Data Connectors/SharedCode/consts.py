"""Module with constants and configurations for the Cyjax IOC integration."""

import os

# *Logging related constants
LOG_LEVEL = os.environ.get("LogLevel", "INFO")
LOGS_STARTS_WITH = "CyjaxIOC"
LOG_FORMAT = "{}(method = {}) : {} : {}"
FUNCTION_NAME = "CyjaxIOCIngestion"

# *Sentinel Upload Indicator API related constants
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")
WORKSPACE_ID = os.environ.get("WORKSPACE_ID", "")
AZURE_AUTHENTICATION_URL = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"
AUTH_SCOPE = "https://management.azure.com/.default"
UPLOAD_INDICATOR_URL = (
    "https://api.ti.sentinel.azure.com/workspaces/{}/"
    "threat-intelligence-stix-objects:upload?api-version=2024-02-01-preview"
)

# *Cyjax API related constants
CYJAX_BASE_URL = os.environ.get("CYJAX_BASE_URL", "https://api.cymon.co/v2")
CYJAX_ACCESS_TOKEN = os.environ.get("CYJAX_ACCESS_TOKEN", "")
CYJAX_IOC_ENDPOINT = "/indicator-of-compromise"
CYJAX_ENRICHMENT_ENDPOINT = "/indicator-of-compromise/enrichment"
CYJAX_PAGE_SIZE = 100
CYJAX_MAX_PAGE = 100
STIX_SOURCE_SYSTEM = "Cyjax-IOCs"
STIX_BATCH_SIZE = 100

# *Checkpoint related constants
CONN_STRING = os.environ.get("AzureWebJobsStorage", "")
FILE_SHARE_NAME = os.environ.get("FILE_SHARE_NAME", "cyjax-ioc")
CHECKPOINT_FILE = "cyjax_ioc_checkpoint"
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "1"))
ENABLE_ENRICHMENT = os.environ.get("ENABLE_ENRICHMENT", "true").lower().strip() == "true"
IOC_QUERY = os.environ.get("IOC_QUERY", "").strip()
INDICATOR_TYPE = os.environ.get("Indicator_Type", "").strip()

# *Error Messages for Exception
UNEXPECTED_ERROR_MSG = "Unexpected error : Error-{}"
HTTP_ERROR_MSG = "HTTP error : Error-{}"
REQUEST_ERROR_MSG = "Request error : Error-{}"
CONNECTION_ERROR_MSG = "Connection error : Error-{}"
KEY_ERROR_MSG = "Key error : Error-{}"
TYPE_ERROR_MSG = "Type error : Error-{}"
VALUE_ERROR_MSG = "Value error : Error-{}"
JSON_DECODE_ERROR_MSG = "JSONDecode error : Error-{}"
TIME_OUT_ERROR_MSG = "Timeout error : Error-{}"
MAX_RETRY_ERROR_MSG = "Max retries exceeded : {} Last exception: {}"

# *Retry and Timeout Configuration
MAX_RETRIES = 3
FUNCTION_APP_TIMEOUT_SECONDS = 570
RETRY_STATUS_CODE = [429, 500, 503, 502]
EXCEPTION_STATUS_CODE = [400, 404, 409]
SENTINEL_429_SLEEP = 60
MAX_SLEEP_TIME = 30
MIN_SLEEP_TIME = 5
BACKOFF_MULTIPLIER = 2
REQUEST_TIMEOUT = 30

# *STIX Indicator
SIGHTINGS_LIMIT = 35
ALLOWED_INDICATOR_TYPES = [
    "URL",
    "Domain",
    "IPv4",
    "IPv6",
    "Hostname",
    "Email",
    "FileHash-SHA1",
    "FileHash-SHA256",
    "FileHash-MD5",
    "FileHash-SSDEEP",
]
