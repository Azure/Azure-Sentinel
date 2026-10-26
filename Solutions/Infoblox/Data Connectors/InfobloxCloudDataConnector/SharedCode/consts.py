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
WORKSPACE_ID = os.environ.get("Workspace_Id", "")

# AAD token scope for the Log Ingestion API, derived by the ARM template from environment().portal
# (e.g. "https://monitor.azure.com/.default" on Azure Public, "https://monitor.azure.us/.default" on Gov Cloud).
SCOPE = os.environ.get("Scope", "https://monitor.azure.com/.default")

LOG_LEVEL = os.environ.get("LogLevel", "INFO")

# *Sentinel Apis
AZURE_AUTHENTICATION_URL = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"
UPLOAD_SENTINEL_INDICATORS_URL = (
    "https://sentinelus.azure-api.net/{}/threatintelligence:upload-indicators"
    "?api-version=2022-07-01"
)

# *Log Ingestion API (DCE/DCR) related constants
# Replaces the legacy HTTP Data Collector API (Workspace_Id/Workspace_Key + HMAC signing, EOL 2026-09-14).
# A single DCE hosts every DCR for this connector (one DCE, max DCRs per DCE - no per-DCE fan-out needed).
DCE_ENDPOINT = os.environ.get("Dce_Endpoint", "")

DCR_ATP_IMMUTABLE_ID = os.environ.get("Dcr_Atp_ImmutableId", "")
DCR_DNS_IMMUTABLE_ID = os.environ.get("Dcr_Dns_ImmutableId", "")
DCR_GEO_IMMUTABLE_ID = os.environ.get("Dcr_Geo_ImmutableId", "")
DCR_INFOBLOX_WEB_CAT_IMMUTABLE_ID = os.environ.get("Dcr_InfobloxWebCat_ImmutableId", "")
DCR_INFORANK_IMMUTABLE_ID = os.environ.get("Dcr_Inforank_ImmutableId", "")
DCR_MALWARE_ANALYSIS_V3_IMMUTABLE_ID = os.environ.get("Dcr_MalwareAnalysisV3_ImmutableId", "")
DCR_NAMESERVER_IMMUTABLE_ID = os.environ.get("Dcr_Nameserver_ImmutableId", "")
DCR_NAMESERVER_MATCHES_IMMUTABLE_ID = os.environ.get("Dcr_NameserverMatches_ImmutableId", "")
DCR_PTR_IMMUTABLE_ID = os.environ.get("Dcr_Ptr_ImmutableId", "")
DCR_RPZ_FEEDS_IMMUTABLE_ID = os.environ.get("Dcr_RpzFeeds_ImmutableId", "")
DCR_RPZ_FEEDS_RECORDS_IMMUTABLE_ID = os.environ.get("Dcr_RpzFeedsRecords_ImmutableId", "")
DCR_THREAT_ACTOR_IMMUTABLE_ID = os.environ.get("Dcr_ThreatActor_ImmutableId", "")
DCR_TLD_RISK_IMMUTABLE_ID = os.environ.get("Dcr_TldRisk_ImmutableId", "")
DCR_WHITELIST_IMMUTABLE_ID = os.environ.get("Dcr_Whitelist_ImmutableId", "")
DCR_WHOIS_IMMUTABLE_ID = os.environ.get("Dcr_Whois_ImmutableId", "")

# table_key (as used by SharedCode.sentinel.ingest_logs) -> {endpoint, immutable_id, stream}
# The "Atp" DCR carries two streams (dossier_atp_CL summary + dossier_atp_threat_CL per-threat rows),
# so both "atp" and "atp_threat" share DCR_ATP_IMMUTABLE_ID but target different stream names.
DCR_STREAMS = {
    "atp": {"endpoint": DCE_ENDPOINT, "immutable_id": DCR_ATP_IMMUTABLE_ID, "stream": "Custom-DossierAtp"},
    "atp_threat": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_ATP_IMMUTABLE_ID,
        "stream": "Custom-DossierAtpThreat",
    },
    "dns": {"endpoint": DCE_ENDPOINT, "immutable_id": DCR_DNS_IMMUTABLE_ID, "stream": "Custom-DossierDns"},
    "geo": {"endpoint": DCE_ENDPOINT, "immutable_id": DCR_GEO_IMMUTABLE_ID, "stream": "Custom-DossierGeo"},
    "infoblox_web_cat": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_INFOBLOX_WEB_CAT_IMMUTABLE_ID,
        "stream": "Custom-DossierInfobloxWebCat",
    },
    "inforank": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_INFORANK_IMMUTABLE_ID,
        "stream": "Custom-DossierInforank",
    },
    "malware_analysis_v3": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_MALWARE_ANALYSIS_V3_IMMUTABLE_ID,
        "stream": "Custom-DossierMalwareAnalysisV3",
    },
    "nameserver": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_NAMESERVER_IMMUTABLE_ID,
        "stream": "Custom-DossierNameserver",
    },
    "nameserver_matches": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_NAMESERVER_MATCHES_IMMUTABLE_ID,
        "stream": "Custom-DossierNameserverMatches",
    },
    "ptr": {"endpoint": DCE_ENDPOINT, "immutable_id": DCR_PTR_IMMUTABLE_ID, "stream": "Custom-DossierPtr"},
    "rpz_feeds": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_RPZ_FEEDS_IMMUTABLE_ID,
        "stream": "Custom-DossierRpzFeeds",
    },
    "rpz_feeds_records": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_RPZ_FEEDS_RECORDS_IMMUTABLE_ID,
        "stream": "Custom-DossierRpzFeedsRecords",
    },
    "threat_actor": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_THREAT_ACTOR_IMMUTABLE_ID,
        "stream": "Custom-DossierThreatActor",
    },
    "tld_risk": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_TLD_RISK_IMMUTABLE_ID,
        "stream": "Custom-DossierTldRisk",
    },
    "whitelist": {
        "endpoint": DCE_ENDPOINT,
        "immutable_id": DCR_WHITELIST_IMMUTABLE_ID,
        "stream": "Custom-DossierWhitelist",
    },
    "whois": {"endpoint": DCE_ENDPOINT, "immutable_id": DCR_WHOIS_IMMUTABLE_ID, "stream": "Custom-DossierWhois"},
}


# *Infoblox related constants
API_TOKEN = os.environ.get("API_token", "")
BASE_URL = os.environ.get("BaseUrl", "") + "{}"
ENDPOINTS = {
    "active_threats_by_type": "/tide/api/data/threats/state/{}",
}
INFOBLOX_CLIENT = "Microsoft_Sentinel-Infoblox"
ACCOUNT_ENDPOINT = "/api/atcfw/v1/account"
CUSTOMER_ID_CHECKPOINT_KEY = "infoblox-customer-id"
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
UNEXPECTED_ERROR_MSG = "Unexpected error : Error-{}"
HTTP_ERROR_MSG = "HTTP error : Error-{}"
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DCR_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# *checkpoint related constants
CONN_STRING = os.environ.get("Connection_String", "")
FILE_SHARE_NAME = os.environ.get("File_Share_Name")
FILE_NAME = os.environ.get("Checkpoint_File_Name", "")
FILE_SHARE_NAME_DATA = os.environ.get("File_Share_Name_For_Data", "")
CHECKPOINT_TABLE_NAME = os.environ.get("Checkpoint_Table_Name", "InfobloxCheckpoints")
CHUNK_SIZE_INDICATOR = 100
MAX_RETRIES = 3
SIZE_OF_CHUNK_TO_INGEST = 20 * 1024 * 1024

# *Extra constants, use for code readability
LOGS_STARTS_WITH = "Infoblox"
HISTORICAL_I_TO_S_FUNCTION_NAME = "InfobloxHistoricalToAzureStorage"
CURRENT_I_TO_S_FUNCTION_NAME = "InfobloxCurrentToAzureStorage"
INDICATOR_FUNCTION_NAME = "ThreatIndicators"

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
