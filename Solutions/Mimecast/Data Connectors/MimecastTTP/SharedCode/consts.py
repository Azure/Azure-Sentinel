"""Module with constants and configurations for the Mimecast integration."""

import os

LOG_LEVEL = os.environ.get("LogLevel", "INFO")
LOGS_STARTS_WITH = "Mimecast"
LOG_FORMAT = "{}(method = {}) : {} : {}"


# *Sentinel related constants
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")
SCOPE = os.environ["SCOPE"]
AZURE_DATA_COLLECTION_ENDPOINT = os.environ["AZURE_DATA_COLLECTION_ENDPOINT"]
DCR_RULE_ID = os.environ["AZURE_DATA_COLLECTION_RULE_ID_MAIN_TABLES"]

# *Mimecast related constants
MIMECAST_CLIENT_ID = os.environ.get("MimecastClientID")
MIMECAST_CLIENT_SECRET = os.environ.get("MimecastClientSecret")
Mimecast_TTP_Attachment_Table_Name = os.environ.get("Mimecast_TTP_Attachment_Table_Name", "Ttp_Attachment")
Mimecast_Ttp_Impersonation_Table_Name = os.environ.get("Mimecast_Ttp_Impersonation_Table_Name", "Ttp_Impersonation")
Mimecast_Ttp_Url_Table_Name = os.environ.get("Mimecast_Ttp_Url_Table_Name", "Ttp_Url")

BASE_URL = os.environ.get("BaseURL", "https://api.services.mimecast.com")
ENDPOINTS = {
    "OAUTH2": "/oauth/token",
    "TTP_URL": "/api/ttp/url/get-logs",
    "SEG_DLP": "/api/dlp/get-logs",
    "TTP_ATTACHMENT": "/api/ttp/attachment/get-logs",
    "TTP_IMPERSONATION": "/api/ttp/impersonation/get-logs",
}

TABLE_NAME = {
    "TTP_URL": Mimecast_Ttp_Url_Table_Name if Mimecast_Ttp_Url_Table_Name else "Ttp_Url",
    "SEG_DLP": "Seg_Dlp",
    "TTP_ATTACHMENT": Mimecast_TTP_Attachment_Table_Name if Mimecast_TTP_Attachment_Table_Name else "Ttp_Attachment",
    "TTP_IMPERSONATION": Mimecast_Ttp_Impersonation_Table_Name if Mimecast_Ttp_Impersonation_Table_Name else "Ttp_Impersonation"
}
TTP_URL_FUNCTION_NAME = "TTP_URL"
TTP_ATTACHMENT_FUNCTION_NAME = "TTP_Attachment"
TTP_IMPERSONATION_FUNCTION_NAME = "TTP_Impersonation"
SEG_DLP_FUNCTION_NAME = "SEG_DLP"


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


# *checkpoint related constants
CONN_STRING = os.environ.get("Connection_String")
FILE_SHARE_NAME = os.environ.get("File_Share_Name", "mimecast-checkpoints")
START_DATE = os.environ.get("StartDate")

# *Extra constants
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_CHUNK_SIZE = 1024 * 1024
MAX_RETRIES = 5
PAGE_SIZE = 500
FUNCTION_APP_TIMEOUT_SECONDS = 570
TIME_DIFFERENCE = 900
DEFAULT_LOOKUP_DAY = 60
SENTINEL_RETRY_COUNT = 3
MAX_TIMEOUT_SENTINEL = 120
INGESTION_ERROR_SLEEP_TIME = 30
EXCEPTION_STATUS_CODE = [400, 403, 409]
RETRY_STATUS_CODE = [429, 500, 503, 502, 509]
MAX_SLEEP_TIME = 30
MIN_SLEEP_TIME = 5
BACKOFF_MULTIPLIER = 2
