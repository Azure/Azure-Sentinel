"""This file contains all constants."""
import os
BASE_URL = os.environ.get("BaseURL")
ENDPOINTS = {
    "authentication": "auth/2/token",
    "get_lists": "account/2/get_lists",
    "add_integration_settings": "integration/1/settings/",
}
LOGS_STARTS_WITH = "DataminrPulseAlerts:"
ALERTS_TABLE_NAME = os.environ.get('AlertsTableName')
RELATEDALERTS_TABLE_NAME = "{}_relatedAlerts"
VULNERABILITY_PRODUCTS_TABLE_NAME = "{}_vulnerabilities_products"
VULNERABILITY_PRODUCTS_RELATEDALERTS_TABLE_NAME = (
    "{}_vulnerabilities_products_relatedAlerts"
)
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.environ.get("LogLevel", "")
DATAMINR_PULSE_THREAT_INTELLIGENCE = "Dataminr Pulse ThreatIntelligence"
AZURE_CLIENT_ID = os.environ.get("Azure_Client_Id")
AZURE_CLIENT_SECRET = os.environ.get("Azure_Client_Secret")
AZURE_TENANT_ID = os.environ.get("Azure_Tenant_Id")
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
SENTINEL_429_SLEEP = 60
