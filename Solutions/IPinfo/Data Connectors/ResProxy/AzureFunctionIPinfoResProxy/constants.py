import os

__all__ = [
    'RESOURCE_ID', 'IPINFO_TOKEN', 'TENANT_ID', 'CLIENT_ID', 'CLIENT_SECRET',
    'LOCATION', 'SUBCRIPTION_ID', 'RESOURCE_GROUP_NAME', 'WORKSPACE_NAME', 
    'RETENTION_IN_DAYS', 'TOTAL_RETENTION_IN_DAYS', 'DATA_COLLECTION_ENDPOINT_NAME', 
    'RESIDENTIAL_PROXY_DCR_NAME', 'RESIDENTIAL_PROXY_TABLE_NAME', 'RESIDENTIAL_PROXY_STREAM_DECLARATION', 
    'AZURE_SCOPE', 'AZURE_BASE_URL', 'IPINFO_BASE_URL', 'MMDB_NAME', 
    'RESIDENTIAL_PROXY_TABLE_SCHEMA', 'RESIDENTIAL_PROXY_TABLE_COLUMNS'
]

# Enviornment Variables
RESOURCE_ID = os.environ["RESOURCE_ID"]
IPINFO_TOKEN = os.environ["IPINFO_TOKEN"]
TENANT_ID = os.environ["TENANT_ID"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
RETENTION_IN_DAYS = os.environ["RETENTION_IN_DAYS"]
TOTAL_RETENTION_IN_DAYS = os.environ["TOTAL_RETENTION_IN_DAYS"]
LOCATION = os.environ["LOCATION"]

parts = RESOURCE_ID.split("/")
SUBCRIPTION_ID = parts[2]
RESOURCE_GROUP_NAME = parts[4]
WORKSPACE_NAME = parts[8]

DATA_COLLECTION_ENDPOINT_NAME = f"ipinfo-logs-ingestion-{WORKSPACE_NAME.lower()}"
RESIDENTIAL_PROXY_DCR_NAME = f"ipinfo_rule_for_RESIDENTIAL_PROXY_tables-{WORKSPACE_NAME.lower()}"
RESIDENTIAL_PROXY_TABLE_NAME = "Ipinfo_RESIDENTIAL_PROXY_CL"
RESIDENTIAL_PROXY_STREAM_DECLARATION = "Custom-Ipinfo_RESIDENTIAL_PROXY_CL"

AZURE_SCOPE = "https://management.azure.com/.default"
AZURE_BASE_URL = f"https://management.azure.com/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft."
IPINFO_BASE_URL = "https://ipinfo.io/data"
MMDB_NAME = "resproxy_30d.mmdb"

RESIDENTIAL_PROXY_TABLE_SCHEMA = {
    "properties": {
        "totalRetentionInDays": TOTAL_RETENTION_IN_DAYS,
        "archiveRetentionInDays": 0,
        "plan": "Analytics",
        "retentionInDaysAsDefault": True,
        "totalRetentionInDaysAsDefault": True,
        "schema": {
            "tableSubType": "DataCollectionRuleBased",
            "name": RESIDENTIAL_PROXY_TABLE_NAME,
            "tableType": "CustomLog",
            "description": "Range based table",
            "columns": [
                {"name": "TimeGenerated", "type": "datetime", "isDefaultDisplay": False, "isHidden": False},
                {"name": "ip", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "service", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "last_seen", "type": "datetime", "isDefaultDisplay": False, "isHidden": False},
                {"name": "percent_days_seen", "type": "int", "isDefaultDisplay": False, "isHidden": False},
            ],
            "standardColumns": [{"name": "TenantId", "type": "guid", "isDefaultDisplay": False, "isHidden": False}],
            "solutions": ["LogManagement"],
            "isTroubleshootingAllowed": True,
        },
        "provisioningState": "Succeeded",
        "retentionInDays": RETENTION_IN_DAYS,
    },
    "id": f"/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.OperationalInsights/workspaces/{WORKSPACE_NAME}/tables/{RESIDENTIAL_PROXY_TABLE_NAME}",
    "name": RESIDENTIAL_PROXY_TABLE_NAME,
}

RESIDENTIAL_PROXY_TABLE_COLUMNS = {
    "columns": [
        {"name": "TimeGenerated", "type": "datetime"},
        {"name": "ip", "type": "string"},
        {"name": "service", "type": "string"},
        {"name": "last_seen", "type": "datetime"},
        {"name": "percent_days_seen", "type": "int"},
    ]
}

