"""Module with constants and configurations for the Infoblox integration."""

import os

# * Dossier consts
DOSSIER_GET_RESULT_FUNCTION_NAME = "DossierGetResult"
DOSSIER_REQUIRED_SOURCE_FUNCTION_NAME = "DossierRequiredSource"
DOSSIER_HTTP_STARTER_FUNCTION_NAME = "HTTPStarterFunction"
DOSSIER_ORCHESTRATOR_FUNCTION_NAME = "DossierOrchestrator"
NUMBER_OF_IOCS = int(os.environ.get("Number_Of_Indicators", "100"))
DOSSIER = "dossier"
DOSSIER_STATUS_MESSAGE = "Click here to view the data"
DOSSIER_ENDPOINTS = {
    "Create_Get": "/tide/api/services/intel/lookup/indicator/{}",
    "Create_Post": "/tide/api/services/intel/lookup/jobs",
    "Status": "/tide/api/services/intel/lookup/jobs/{}/pending",
    "Result": "/tide/api/services/intel/lookup/jobs/{}/results",
}
SOURCES = {
    "ip": [
        "atp",
        "geo",
        "malware_analysis_v3",
        "ptr",
        "rpz_feeds",
        "whitelist",
        "whois",
    ],
    "host": [
        "atp",
        "dns",
        "geo",
        "infoblox_web_cat",
        "inforank",
        "malware_analysis_v3",
        "nameserver",
        "rpz_feeds",
        "threat_actor",
        "tld_risk",
        "whitelist",
        "whois",
    ],
    "url": [
        "atp",
        "infoblox_web_cat",
        "malware_analysis_v3",
        "tld_risk",
        "whitelist",
    ],
    "hash": [
        "atp",
        "malware_analysis_v3",
    ],
    "email": [
        "atp",
    ],
}

# *Sentinel related constants
AZURE_CLIENT_ID = os.environ.get("Azure_Client_Id", "")
AZURE_CLIENT_SECRET = os.environ.get("Azure_Client_Secret", "")
AZURE_TENANT_ID = os.environ.get("Azure_Tenant_Id", "")
WORKSPACE_KEY = os.environ.get("Workspace_Key", "")
WORKSPACE_ID = os.environ.get("Workspace_Id", "")

LOG_LEVEL = os.environ.get("LogLevel", "INFO")

# *Sentinel Apis
AZURE_AUTHENTICATION_URL = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"
UPLOAD_SENTINEL_INDICATORS_URL = (
    "https://sentinelus.azure-api.net/{}/threatintelligence:upload-indicators"
    "?api-version=2022-07-01"
)


# *Infoblox related constants
API_TOKEN = os.environ.get("API_token", "")
BASE_URL = os.environ.get("BaseUrl", "") + "{}"
ENDPOINTS = {
    "active_threats_by_type": "/tide/api/data/threats/state/{}",
}
MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_CHUNK_SIZE = 1024 * 1024

HISTORICAL_TIME_INTERVAL = int(os.environ.get("HISTORICAL_TIME_INTERVAL", "-3"))
CURRENT_TIME_INTERVAL = int(os.environ.get("CURRENT_TIME_INTERVAL", "1"))
HISTORICAL_START_DATE = os.environ.get("Historical_Start_Date", "")

TYPE = os.environ.get("ThreatType", "")
FIELDS = (
    "id,type,ip,url,tld,email,hash,hash_type,host,domain,profile,property,class,"
    "threat_level,confidence,detected,received,imported,expiration,dga,up,"
    "threat_score,threat_score_rating,confidence_score,confidence_score_rating,"
    "risk_score,risk_score_rating,extended"
)
CONFIDENCE_THRESHOLD = int(os.environ.get("Confidence_Threshold", "80"))
THREAT_LEVEL = int(os.environ.get("Threat_Level", "80"))
FILE_NAME_PREFIX_COMPLETED = "infoblox_completed"
FAILED_INDICATOR_FILE_PREFIX = "infoblox_failed"
FAILED_INDICATORS_TABLE_NAME = "Infoblox_Failed_Indicators"
UNEXPECTED_ERROR_MSG = "Unexpected error : Error-{}"
HTTP_ERROR_MSG = "HTTP error : Error-{}"
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

# *checkpoint related constants
CONN_STRING = os.environ.get("Connection_String", "")
FILE_SHARE_NAME = os.environ.get("File_Share_Name")
FILE_NAME = os.environ.get("Checkpoint_File_Name", "")
FILE_SHARE_NAME_DATA = os.environ.get("File_Share_Name_For_Data", "")
CHUNK_SIZE_INDICATOR = 100
MAX_RETRIES = 3
SIZE_OF_CHUNK_TO_INGEST = 20 * 1024 * 1024

# *Extra constants, use for code readability
LOGS_STARTS_WITH = "Infoblox"
HISTORICAL_I_TO_S_FUNCTION_NAME = "InfobloxHistoricalToAzureStorage"
CURRENT_I_TO_S_FUNCTION_NAME = "InfobloxCurrentToAzureStorage"
INDICATOR_FUNCTION_NAME = "ThreatIndicators"
FAILED_INDICATOR_FUNCTION_NAME = "FailedThreatIndicators"

# *ParseRawIndicatorsData consts
PARSE_RAW_JSON_DATA_FUNCTION_NAME = "InfoBloxParseRawJsonData"
FILE_NAME_PREFIX = "infoblox_raw"
TIME_BUFFER_RAW_EPOCH_VALUE = 600
MAX_FILE_AGE_FOR_INDICATORS = 900
TIMEOUT = 540
FUNCTION_APP_TIMEOUT_SECONDS = 570
JSON_START_INDEX = 10
SLEEP_TIME = 10

# *Log related constants
LOG_FORMAT = "{}(method = {}) : {} : {}"
