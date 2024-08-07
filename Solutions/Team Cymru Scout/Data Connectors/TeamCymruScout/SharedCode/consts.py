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
IPv4_REGEX = r"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
IPv6_REGEX = r"^(([0-9A-Fa-f]{1,4}:){7,7}[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,7}:|([0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2}|([0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3}|([0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4}|([0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5}|[0-9A-Fa-f]{1,4}:((:[0-9A-Fa-f]{1,4}){1,6})|::(?:ffff(:0{1,4}){0,1}:){0,1}((?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"

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
