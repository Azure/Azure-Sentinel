"""This file contains all constants."""
import os

# To do: in every file, just import consts.py file, rather than importing all constants.
COFENSE_BASE_URL = os.environ.get("BaseURL", "").rstrip("/")
ENDPOINTS = {
    "authentication": "/oauth/token",
    "get_lists": "/api/public/v2/threat_indicators",
}
WORKSPACE_ID = os.environ.get("WorkspaceID")
WORKSPACE_KEY = os.environ.get("WorkspaceKey")
REPORTS_TABLE_NAME = os.environ.get("Reports_Table_name")
COFENSE_CLIENT_ID = os.environ.get("Cofense_Client_Id", "")
COFENSE_CLIENT_SECRET = os.environ.get("Cofense_Client_Secret", "")
AZURE_CLIENT_ID = os.environ.get("Azure_Client_Id", "")
AZURE_CLIENT_SECRET = os.environ.get("Azure_Client_Secret", "")
AZURE_TENANT_ID = os.environ.get("Azure_Tenant_Id", "")
AZURE_AUTHENTICATION_URL = "https://login.microsoftonline.com/{}/oauth2/token"
CREATE_SENTINEL_INDICATORS_URL = (
    "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers"
    "/Microsoft.OperationalInsights/workspaces/{workspaceName}/providers/Microsoft.SecurityInsights/threatIntelligence"
    "/main/createIndicator?api-version=2022-12-01-preview"
)
AZURE_RESOURCE_GROUP = os.environ.get("Azure_Resource_Group_Name", "")
AZURE_WORKSPACE_NAME = os.environ.get("Azure_Workspace_Name", "")
AZURE_SUBSCRIPTION_ID = os.environ.get("Azure_Subscription_Id", "")
CONNECTION_STRING = os.environ.get("AzureWebJobsStorage", "")
LOGS_STARTS_WITH = "COFENSE TRIAGE : "
COFENSE_TO_SENTINEL = "CofenseToSentinel"
PROXY_USERNAME = os.environ.get("Proxy_Username", "")
PROXY_PASSWORD = os.environ.get("Proxy_Password", "")
PROXY_URL = os.environ.get("Proxy_URL", "")
PROXY_PORT = os.environ.get("Proxy_Port", "")
QUERY_SENTINEL_INDICATORS_URL = (
    "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers"
    "/Microsoft.OperationalInsights/workspaces/{workspaceName}/providers/Microsoft.SecurityInsights/threatIntelligence"
    "/main/queryIndicators?api-version=2022-12-01-preview"
)
QUERY_SENTINEL_PAGESIZE = 100
COFENSE_POST_INDICATOR_URL = COFENSE_BASE_URL + "/api/public/v2/threat_indicators"
COFENSE_UPDATE_INDICATOR_URL = COFENSE_BASE_URL + "/api/public/v2/threat_indicators/"
SENTINEL_TO_COFENSE = "SentinelToCofense"
COFENSE_429_SLEEP = 300
SENTINEL_429_SLEEP = 60
SENTINEL_SOURCE_PREFIX = "Sentinel : "
COFENSE_SOURCE_PREFIX = "Cofense : "
COFENSE_PAGE_SIZE = 100
COFENSE_PAGE_NUMBER = 1
PROXY_REQUEST = "http"
SENTINEL_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
DATETIMEFORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
THREAT_LEVEL_BENIGN = 1
THREAT_LEVEL_INTERMEDIATE = 33
THREAT_LEVEL_SUSPICIOUS = 75
THREAT_LEVEL_MALICIOUS = 100
SCHEDULE = os.environ.get("Schedule", "")
NON_COFENSE_THROTTLE_LIMIT = os.environ.get(
    "Throttle_Limit_For_Non_Cofense_Indicators", ""
)
DEFENDER_POST_INDICATOR_URL = "https://api.securitycenter.microsoft.com/api/indicators"
SENTINEL_TO_DEFENDER = "SentinelToDefender"
DEFENDER_429_SLEEP = 60
DEFENDER_CREATE_INDICATOR_DESCRIPTION = "Cofense Triage Phishing Threat Indicator."
THREAT_LEVEL = os.environ.get("Threat_Level", "")
THREAT_LEVEL_FILTER_BENIGN = "Benign"
THREAT_LEVEL_FILTER_SUSPICIOUS = "Suspicious"
THREAT_LEVEL_FILTER_MALICIOUS = "Malicious"
