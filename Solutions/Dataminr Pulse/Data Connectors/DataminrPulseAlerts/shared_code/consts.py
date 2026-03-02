"""This file contains all constants."""

import os

BASE_URL = os.environ.get("BaseURL")
ENDPOINTS = {
    "authentication": "auth/2/token",
    "get_lists": "account/2/get_lists",
    "add_integration_settings": "integration/1/settings",
}
LOGS_STARTS_WITH = "DataminrPulseAlerts:"
ALERTS_TABLE_NAME = os.environ.get("AlertsTableName", "DataminrPulse_Alerts")
RELATEDALERTS_TABLE_NAME = "{}_relAlerts"
VULNERABILITY_PRODUCTS_TABLE_NAME = "{}_vuln_prod"
VULNERABILITY_PRODUCTS_RELATEDALERTS_TABLE_NAME = (
    "{}_vuln_prod_relAlert"
)
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.environ.get("LogLevel", "")
DATAMINR_PULSE_THREAT_INTELLIGENCE = "Dataminr Pulse ThreatIntelligence"
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
SCOPE = os.environ["SCOPE"]
AZURE_DATA_COLLECTION_ENDPOINT = os.environ["AZURE_DATA_COLLECTION_ENDPOINT"]
DCR_RULE_ID = os.environ["AZURE_DATA_COLLECTION_RULE_ID_MAIN_TABLES"]
CREATE_SENTINEL_INDICATORS_URL = (
    "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups"
    "/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}"
    "/providers/Microsoft.SecurityInsights/threatIntelligence/main/createIndicator?api-version=2023-03-01-preview"
)
AZURE_AUTHENTICATION_URL = "https://login.microsoftonline.com/{}/oauth2/token"
AZURE_RESOURCE_GROUP = os.environ.get("Azure_Resource_Group_Name", "")
AZURE_WORKSPACE_NAME = os.environ.get("Azure_Workspace_Name", "")
AZURE_SUBSCRIPTION_ID = os.environ.get("Azure_Subscription_Id", "")
CONN_STRING = os.environ.get("AzureWebJobsStorage")
MS_SHARE_NAME = "dataminr-pulse"
RETRY_FAILED_INDICATORS = "Retry Failed Indicators"
FAILED_INDICATORS_TABLE_NAME = "Failed_Indicators"
WORKSPACE_ID = os.environ.get("WorkspaceID")
WORKSPACE_KEY = os.environ.get("WorkspaceKey")
LOG_ANALYTICS_URL = os.environ.get("logAnalyticsUri")
SENTINEL_429_SLEEP = 60
AUTH_RESOURCE_URL = "https://management.azure.com"

if ".us" in LOG_ANALYTICS_URL:
    AUTH_RESOURCE_URL = "https://management.usgovcloudapi.net"
    AZURE_AUTHENTICATION_URL = AZURE_AUTHENTICATION_URL.replace(".com", ".us")
    CREATE_SENTINEL_INDICATORS_URL = (
        "https://management.usgovcloudapi.net/subscriptions/{subscriptionId}/resourceGroups"
        "/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}"
        "/providers/Microsoft.SecurityInsights/threatIntelligence/main/createIndicator?api-version=2023-03-01-preview"
    )
