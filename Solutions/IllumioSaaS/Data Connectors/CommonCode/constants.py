import os

# AWS config
AWS_KEY = os.environ["AWS_KEY"]
AWS_SECRET = os.environ["AWS_SECRET"]
AWS_REGION_NAME = os.environ["AWS_REGION_NAME"]
SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]
VISIBILITY_TIMEOUT = 1800
LINE_SEPARATOR = os.environ.get(
    "lineSeparator", "[\n\r\x0b\v\x0c\f\x1c\x1d\x85\x1e\u2028\u2029]+"
)  # used in aws_queue and queue trigger.py
MAX_SCRIPT_EXEC_TIME_MINUTES = int(os.environ.get("MAX_SCRIPT_EXEC_TIME_MINUTES", 10))
SQS_FILES_READ_LIMIT = int(os.environ.get("SQS_FILES_READ_LIMIT", 200))

# PCE config
API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
PCE_FQDN = os.environ["PCE_FQDN"]
PORT = int(os.environ.get("PCE_PORT", 443))
ORG_ID = os.environ["ORG_ID"]
MAX_WORKLOADS = os.environ.get("MAX_WORKLOADS", 100000)
LOGS_TO_CONSUME = os.environ.get("logTypes", "all").lower()
NETWORK_TRAFFIC_TO_CONSUME = os.environ.get("networkTrafficLogTypes", "All").lower()
FLOW_EVENTS = "Flow Summaries"
AUDIT_EVENTS = "Auditable Events"
ALLOWED_TRAFFIC = "allowed"
POTENTIALLY_BLOCKED_TRAFFIC = "potentially_blocked"
BLOCKED_TRAFFIC = "blocked"
UNKNOWN_TRAFFIC = "unknown"
ALL_TRAFFIC = "all"

# Azure config
AZURE_TENANT_ID = os.environ["AZURE_TENANT_ID"]
AZURE_CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
AZURE_CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
DCE_ENDPOINT = os.environ["DCE_ENDPOINT"]
DCR_ID = os.environ["DCR_ID"]
LOG_ANALYTICS_URI = os.environ["LOG_ANALYTICS_URI"]
WORKLOADS_API_LOGS_CUSTOM_TABLE = os.environ["WORKLOADS_API_LOGS_CUSTOM_TABLE"]
FLOW_LOGS_CUSTOM_TABLE = os.environ["FLOW_LOGS_CUSTOM_TABLE"]
AUDIT_LOGS_CUSTOM_TABLE = os.environ["AUDIT_LOGS_CUSTOM_TABLE"]
WORKSPACE_ID = os.environ["WORKSPACE_ID"]
AZURE_STORAGE_CONNECTION_STRING = os.environ["AzureWebJobsStorage"]
MAX_QUEUE_MESSAGES_MAIN_QUEUE = int(os.environ.get("MAX_QUEUE_MESSAGES_MAIN_QUEUE", 80))

# Azure Storage Queue
AZURE_STORAGE_PRIMARY_QUEUE = "python-queue-items"
AZURE_STORAGE_BACKLOG_QUEUE = "python-queue-items-backlog"