"""This file contains all constants."""
import os

COFENSE_BASE_URL = os.environ.get("BaseURL", "https://www.threathq.com/apiv1")
ENDPOINTS = {
    "search_indicators": "/indicator/search",
    "get_malware": "/threat/malware/{threat_id}",
}
LOGS_STARTS_WITH = "COFENSE Intelligence : "
LOG_LEVEL = os.environ.get("LogLevel", "")
API_TIMEOUT = 20
COFENSE_TO_SENTINEL = "CofenseIntelligenceToSentinel"
COFENSE_USERNAME = os.environ.get("Cofense_Username", "")
COFENSE_PASSWORD = os.environ.get("Cofense_Password", "")
AZURE_CLIENT_ID = os.environ.get("Azure_Client_Id", "")
AZURE_CLIENT_SECRET = os.environ.get("Azure_Client_Secret", "")
AZURE_TENANT_ID = os.environ.get("Azure_Tenant_Id", "")
AZURE_AUTHENTICATION_URL = "https://login.microsoftonline.com/{}/oauth2/token"
SENTINEL_TO_DEFENDER = "SentinelToDefender"
COFENSE_429_SLEEP = 300
COFENSE_PAGE_SIZE = 100
CONNECTION_STRING = os.environ.get("AzureWebJobsStorage", "")
DEFENDER_CHECKPOINT_FILE_PATH = "Defender_checkpoint"
MS_SHARE_NAME = "cofense-intelligence"


QUERY_SENTINEL_INDICATORS_URL = (
    "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers"
    "/Microsoft.OperationalInsights/workspaces/{workspaceName}/providers/Microsoft.SecurityInsights/threatIntelligence"
    "/main/queryIndicators?api-version=2022-12-01-preview"
)
CREATE_SENTINEL_INDICATORS_URL = (
    "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups"
    "/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}"
    "/providers/Microsoft.SecurityInsights/threatIntelligence/main/createIndicator?api-version=2023-03-01-preview"
)
AZURE_RESOURCE_GROUP = os.environ.get("Azure_Resource_Group_Name", "")
AZURE_WORKSPACE_NAME = os.environ.get("Azure_Workspace_Name", "")
AZURE_SUBSCRIPTION_ID = os.environ.get("Azure_Subscription_Id", "")
SENTINEL_429_SLEEP = 60
IS_DEFENDER_USER = os.environ.get("SendCofenseIndicatorToDefender", "")
SCHEDULE = os.environ.get("Schedule", "")
QUERY_SENTINEL_PAGESIZE = 100
IMPACT_NONE = 1
IMPACT_MINOR = 30
IMPACT_MODERATE = 50
IMPACT_MEDIUM = 70
IMPACT_MAJOR = 100
FIFTEEN_DAYS = 1209600

DEFENDER_429_SLEEP = 60
SENTINEL_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
DEFENDER_POST_INDICATOR_URL = "https://api.securitycenter.microsoft.com/api/indicators"
COFENSE_SOURCE_PREFIX = "Cofense Intelligence"


IS_PROXY_REQUIRED = os.environ.get("RequireProxy", "")
PROXY_REQUEST = "http"
PROXY_USERNAME = os.environ.get("Proxy_Username", "")
PROXY_PASSWORD = os.environ.get("Proxy_Password", "")
PROXY_URL = os.environ.get("Proxy_URL", "")
PROXY_PORT = os.environ.get("Proxy_Port", "")

# Malware Data Connector Specific Constants
WORKSPACE_ID = os.environ.get("WorkspaceID")
WORKSPACE_KEY = os.environ.get("WorkspaceKey")
MALWARE_DATA_TABLE_NAME = os.environ.get("Malware_Data_Table_name", "Malware_Data")
COFENSE_MALWARE_DATA_TO_LOG_ANALYTICS = "Malware DataConnector"
FUNCTION_APP_NAME = os.environ.get("Function_App_Name")

RETRY_FAILED_INDICATORS = "Retry Failed Indicators"
FAILED_INDICATORS_TABLE_NAME = "Failed_Indicators"

#Download Threat Reports function name
DOWNLOAD_THREAT_REPORTS = 'DownloadThreatReports'
