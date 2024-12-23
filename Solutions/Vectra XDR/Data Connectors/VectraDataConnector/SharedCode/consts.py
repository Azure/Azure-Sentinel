"""This file contains all constants."""

import os

LOGS_STARTS_WITH = "Vectra : "
DETECTIONS_NAME = "Detections"
AUDITS_NAME = "Audits"
ENTITY_SCORING_NAME = "Entity Scoring"
HOST_ENTITIES_NAME = "Host-Entities"
ACCOUNT_ENTITIES_NAME = "Account-Entities"
ENTITY_SCORING_ACCOUNT_NAME = "Entity Scoring : Account"
ENTITY_SCORING_HOST_NAME = "Entity Scoring : Host"
LOCKDOWN_NAME = "Lockdown"
DEFAULT_LOG_LEVEL = 20
OAUTH2_ENDPOINT = "/oauth2/token"
API_TIMEOUT = 180
SENTINEL_ACCEPTABLE_CODES = list(range(200, 300))
PAGE_SIZE = 100

# Environment Variables of Microsoft Sentinel
KEYVAULT_NAME = os.environ.get("KeyVaultName")
WORKSPACE_ID = os.environ.get("WorkspaceID")
WORKSPACE_KEY = os.environ.get("WorkspaceKey")
CONNECTION_STRING = os.environ.get("AzureWebJobsStorage")
BASE_URL = os.environ.get("BaseURL", "").strip("/ ")
HEALTH_CLIENT_ID = os.environ.get("Health_Client_Id", "").strip()
HEALTH_CLIENT_SECRET = os.environ.get("Health_Client_Secret_Key", "").strip()
ENTITY_SCORING_CLIENT_ID = os.environ.get("Entity_Scoring_Client_Id", "").strip()
ENTITY_SCORING_CLIENT_SECRET = os.environ.get(
    "Entity_Scoring_Client_Secret_Key", ""
).strip()
DETECTIONS_CLIENT_ID = os.environ.get("Detections_Client_Id", "").strip()
DETECTIONS_CLIENT_SECRET = os.environ.get("Detections_Client_Secret_Key", "").strip()
AUDIT_CLIENT_ID = os.environ.get("Audit_Client_Id", "").strip()
AUDIT_CLIENT_SECRET = os.environ.get("Audit_Client_Secret_Key", "").strip()
LOCKDOWN_CLIENT_ID = os.environ.get("Lockdown_Client_Id", "").strip()
LOCKDOWN_CLIENT_SECRET = os.environ.get("Lockdown_Client_Secret_Key", "").strip()
HOST_ENTITY_CLIENT_ID = os.environ.get("Host_Entity_Client_Id", "").strip()
HOST_ENTITY_CLIENT_SECRET = os.environ.get("Host_Entity_Client_Secret_Key", "").strip()
START_TIME = os.environ.get("StartTime", "")
DETECTIONS_TABLE_NAME = os.environ.get("Detections_Table_Name")
AUDITS_TABLE_NAME = os.environ.get("Audits_Table_Name")
ENTITY_SCORING_TABLE_NAME = os.environ.get("Entity_Scoring_Table_Name")
LOG_LEVEL = os.environ.get("LogLevel", "")
DETECTIONS_ENDPOINT = "/api/v3.3/events/detections"
ENTITY_SCORING_ENDPOINT = "/api/v3.3/events/entity_scoring"
USER_AGENT = "Vectra-Sentinel-2.0.0"
LOCKDOWN_TABLE_NAME = os.environ.get("Lockdown_Table_Name")
LOCKDOWN_ENDPOINT = "/api/v3.3/lockdown"
HEALTH_NAME = "Health"
HEALTH_TABLE_NAME = os.environ.get("Health_Table_Name")
HEALTH_ENDPOINT = "/api/v3.3/health"
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
INCLUDE_SCORE_DECREASE = os.environ.get("IncludeScoreDecrease").lower()
ENTITIES_ENDPOINT = "/api/v3.3/entities"
ASSIGNMENT_ENDPOINT = "/api/v3.3/assignments"
ENTITIES_TABLE_NAME = os.environ.get("Entities_Table_Name")
ACCOUNT_ENTITY_CLIENT_ID = os.environ.get("Account_Entity_Client_Id", "").strip()
ACCOUNT_ENTITY_CLIENT_SECRET = os.environ.get(
    "Account_Entity_Client_Secret_Key", ""
).strip()
FUNCTION_APP_NAME = os.environ.get("Function_App_Name")
RESOURCE_GROUP = os.environ.get("Azure_Resource_Group_Name")
SUBSCRIPTION_ID = os.environ.get("Azure_Subscription_Id")
AZURE_AUTHENTICATION_URL = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"
AZURE_AUTHENTICATION_SCOPE = "https://management.azure.com/.default"
DISABLE_FUNCTION_APP_URL = ("https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/"
                            "Microsoft.Web/sites/{}/stop?api-version=2023-01-01")
