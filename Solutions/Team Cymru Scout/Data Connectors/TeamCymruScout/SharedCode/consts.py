"""This file contains constants require for Team Cymru Scout Data Connector."""

import os

# API ENDPOINTS
IP_FOUNDATION_ENDPOINT = "/api/scout/ip/foundation"
IP_DETAILS_ENDPOINT = "/api/scout/ip/{}/details"
SEARCH_ENDPOINT = "/api/scout/search"
ACCOUNT_USAGE_ENDPOINT = "/api/scout/usage"

# Environment Variables
CYMRU_SCOUT_BASE_URL = os.environ.get("CymruScoutBaseURL")
AUTHENTICATION_TYPE = os.environ.get("AuthenticationType")
USERNAME = os.environ.get("TeamCymruScoutUsername")
PASSWORD = os.environ.get("TeamCymruScoutPassword")
API_KEY = os.environ.get("APIKey")
IP_VALUES = os.environ.get("IPValues")
DOMAIN_VALUES = os.environ.get("DomainValues")
API_TYPE = os.environ.get("APIType")
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
WORKSPACE_ID = os.environ.get("WorkspaceID")
WORKSPACE_KEY = os.environ.get("WorkspaceKey")
IP_TABLE_NAME = os.environ.get("IPTableName")
DOMAIN_TABLE_NAME = os.environ.get("DomainTableName")
ACCOUNT_USAGE_TABLE_NAME = os.environ.get("AccountUsageTableName")
LOG_LEVEL = os.environ.get("LogLevel")
CONN_STRING = os.environ.get("AzureWebJobsStorage")

# regex
DOMAIN_REGEX = r"^(?:[a-zA-Z0-9-]+(?:\[\.\]|\.))+[a-zA-Z]{2,}(?:\s*,\s*(?:[a-zA-Z0-9-]+(?:\[\.\]|\.))+[a-zA-Z]{2,})*$"

# Other Constants
IP_WATCHLIST_ALIAS = "TeamCymruScoutIPData"
DOMAIN_WATCHLIST_ALIAS = "TeamCymruScoutDomainData"
DOMAIN_QUERY = """_GetWatchlist('{}')
    | sort by domain asc
    | project domain""".format(
    DOMAIN_WATCHLIST_ALIAS
)
IP_QUERY = """_GetWatchlist('{}')
    | sort by ip asc
    | project ip""".format(
    IP_WATCHLIST_ALIAS
)
LOGS_STARTS_WITH = "TeamCymruScout:"
DEFAULT_LOG_LEVEL = "INFO"
POST_CHUNK_SIZE = 100
FOUNDATION_CHUNK_SIZE = 10
INGESTION_ERROR_SLEEP_TIME = 30
SENTINEL_RETRY_COUNT = 5
MAX_TIMEOUT_SENTINEL = 180
RETRY_STATUS_CODES = [429, 500, 503]


# Error Messages for Exception
JSON_DECODE_ERROR_MSG = "JSONDecode error : Error-{}"
TIME_OUT_ERROR_MSG = "Timeout error : Error-{}"
CONNECTION_ERROR_MSG = "Connection error : Error-{}"
REQUEST_ERROR_MSG = "Request error : Error-{}"
UNEXPECTED_ERROR_MSG = "Unexpected error : Error-{}"
HTTP_ERROR_MSG = "HTTP error : Error-{}"
