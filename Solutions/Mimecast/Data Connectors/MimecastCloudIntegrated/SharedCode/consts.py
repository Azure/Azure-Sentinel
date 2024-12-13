"""Module with constants and configurations for the Mimecast integration."""

import os

LOG_LEVEL = os.environ.get("LogLevel", "INFO")
LOGS_STARTS_WITH = "Mimecast"
LOG_FORMAT = "{}(method = {}) : {} : {}"


# *Sentinel related constants
AZURE_CLIENT_ID = os.environ.get("Azure_Client_Id", "")
AZURE_CLIENT_SECRET = os.environ.get("Azure_Client_Secret", "")
AZURE_TENANT_ID = os.environ.get("Azure_Tenant_Id", "")
WORKSPACE_KEY = os.environ.get("Workspace_Key", "")
WORKSPACE_ID = os.environ.get("Workspace_Id", "")

# *Mimecast related constants
MIMECAST_CLIENT_ID = os.environ.get("Mimecast_client_id")
MIMECAST_CLIENT_SECRET = os.environ.get("Mimecast_client_secret")

BASE_URL = os.environ.get("BaseUrl", "https://api.services.mimecast.com")
ENDPOINTS = {
    "OAUTH2": "/oauth/token",
    "TTP_URL": "/api/ttp/url/get-logs",
    "SEG_DLP": "/api/dlp/get-logs",
    "SEG_CG": "/siem/v1/batch/events/cg",
    "CI": "/siem/v1/batch/events/ci",
}

TABLE_NAME = {
    "TTP_URL": "Ttp_Url",
    "SEG_DLP": "Seg_Dlp",
    "SEG_CG": "Seg_Cg_3",
    "CI": "Cloud_Integrated",
}
TTP_URL_FUNCTION_NAME = "TTP_URL"
SEG_DLP_FUNCTION_NAME = "SEG_DLP"
SEG_CG_FUNCTION_NAME = "SEG_CG"
CLOUD_INTEGRATED_FUNCTION_NAME = "CLOUD_INTEGRATED"

CI_TYPES = "entities,mailflow,urlclick"

# *Error Messages for Exception
UNEXPECTED_ERROR_MSG = "Unexpected error : Error-{}"
UNEXPECTED_ERROR_TASK_MSG = "Unexpected error : Error-{}, task = {}"
HTTP_ERROR_MSG = "HTTP error : Error-{}"
REQUEST_ERROR_MSG = "Request error : Error-{}"
CONNECTION_ERROR_MSG = "Connection error : Error-{}"
KEY_ERROR_MSG = "Key error : Error-{}"
TYPE_ERROR_MSG = "Type error : Error-{}"
VALUE_ERROR_MSG = "Value error : Error-{}"
JSON_DECODE_ERROR_MSG = "JSONDecode error : Error-{}"
CLIENT_ERROR_MSG = "Client error : Error-{}"
TIME_OUT_ERROR_MSG = "Timeout error : Error-{}"
MAX_RETRY_ERROR_MSG = "Max retries exceeded : {} Last exception: {}"


# *checkpoint related constants
CONN_STRING = os.environ.get("Connection_String")
FILE_SHARE_NAME = os.environ.get("File_Share_Name", "mimecast-checkpoints")
START_DATE = os.environ.get("Start_Date")

# *Extra constants
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_CHUNK_SIZE = 1024 * 1024
MAX_RETRIES = 5
MAX_RETRIES_ASYNC = 2
PAGE_SIZE = 500
DEFAULT_LOOKUP_DAY = 60
FUNCTION_APP_TIMEOUT_SECONDS = 540
TIME_DIFFERENCE = 900
ASYNC_PAGE_SIZE = 10
SENTINEL_RETRY_COUNT = 3
MAX_TIMEOUT_SENTINEL = 120
INGESTION_ERROR_SLEEP_TIME = 30
EXCEPTION_STATUS_CODE = [400, 403, 409]
RETRY_STATUS_CODE = [429, 500, 503, 502, 509]
MAX_SLEEP_TIME = 30
MIN_SLEEP_TIME = 5
BACKOFF_MULTIPLIER = 2
