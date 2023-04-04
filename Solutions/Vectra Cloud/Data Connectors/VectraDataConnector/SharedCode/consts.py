"""This file contains all constants."""
import os

LOGS_STARTS_WITH = "Vectra : "
ACCOUNT_DETECTION_NAME = "Account Detection"
AUDITS_NAME = "Audits"
ENTITY_SCORING_NAME = "Entity Scoring"
DEFAULT_LOG_LEVEL = 20
OAUTH2_ENDPOINT = "/oauth2/token"
API_TIMEOUT = 180
SENTINEL_ACCEPTABLE_CODES = list(range(200, 300))

# Environment Variables of Microsoft Sentinel
WORKSPACE_ID = os.environ.get("WorkspaceID")
WORKSPACE_KEY = os.environ.get("WorkspaceKey")
CONNECTION_STRING = os.environ.get("AzureWebJobsStorage")
BASE_URL = os.environ.get("BaseURL", "").strip("/ ")
CLIENT_ID = os.environ.get("ClientId", "").strip()
CLIENT_SECRET = os.environ.get("ClientSecretKey", "").strip()
START_TIME = os.environ.get("StartTime", "")
ACCOUNT_DETECTION_TABLE_NAME = os.environ.get("Account_Detection_Table_Name")
AUDITS_TABLE_NAME = os.environ.get("Audits_Table_Name")
ENTITY_SCORING_TABLE_NAME = os.environ.get("Entity_Scoring_Table_Name")
LOG_LEVEL = os.environ.get("LogLevel", "")
