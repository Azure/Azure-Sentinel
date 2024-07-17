import os

__all__ = [
    'RESOURCE_ID', 'IPINFO_TOKEN', 'TENANT_ID', 'CLIENT_ID', 'CLIENT_SECRET',
    'LOCATION', 'SUBCRIPTION_ID', 'RESOURCE_GROUP_NAME', 'WORKSPACE_NAME', 
    'RETENTION_IN_DAYS', 'TOTAL_RETENTION_IN_DAYS', 'DATA_COLLECTION_ENDPOINT_NAME', 
    'PRIVACY_DCR_NAME', 'PRIVACY_TABLE_NAME', 'PRIVACY_STREAM_DECLARATION', 
    'AZURE_SCOPE', 'AZURE_BASE_URL', 'IPINFO_BASE_URL', 'MMDB_NAME', 
    'PRIVACY_TABLE_SCHEMA', 'PRIVACY_TABLE_COLUMNS'
]

# Enviornment Virables
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

DATA_COLLECTION_ENDPOINT_NAME = "ipinfo-logs-ingestion"
PRIVACY_DCR_NAME = "ipinfo_rule_for_privacy_tables"
PRIVACY_TABLE_NAME = "Ipinfo_Privacy_CL"
PRIVACY_STREAM_DECLARATION = "Custom-Ipinfo_Privacy_CL"

AZURE_SCOPE = "https://management.azure.com/.default"
AZURE_BASE_URL = f"https://management.azure.com/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft."
IPINFO_BASE_URL = "https://ipinfo.io/data"
MMDB_NAME = "standard_privacy.mmdb"

PRIVACY_TABLE_SCHEMA = {
    "properties": {
        "totalRetentionInDays": TOTAL_RETENTION_IN_DAYS,
        "archiveRetentionInDays": 0,
        "plan": "Analytics",
        "retentionInDaysAsDefault": True,
        "totalRetentionInDaysAsDefault": True,
        "schema": {
            "tableSubType": "DataCollectionRuleBased",
            "name": PRIVACY_TABLE_NAME,
            "tableType": "CustomLog",
            "description": "Range based table",
            "columns": [
                {"name": "hosting", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "proxy", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "relay", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "service", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "tor", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "vpn", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "ip_range", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "TimeGenerated", "type": "datetime", "isDefaultDisplay": False, "isHidden": False},
            ],
            "standardColumns": [{"name": "TenantId", "type": "guid", "isDefaultDisplay": False, "isHidden": False}],
            "solutions": ["LogManagement"],
            "isTroubleshootingAllowed": True,
        },
        "provisioningState": "Succeeded",
        "retentionInDays": RETENTION_IN_DAYS,
    },
    "id": f"/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.OperationalInsights/workspaces/{WORKSPACE_NAME}/tables/{PRIVACY_TABLE_NAME}",
    "name": PRIVACY_TABLE_NAME,
}

PRIVACY_TABLE_COLUMNS = {
    "columns": [
        {"name": "TimeGenerated", "type": "datetime"},
        {"name": "hosting", "type": "string"},
        {"name": "proxy", "type": "string"},
        {"name": "relay", "type": "string"},
        {"name": "service", "type": "string"},
        {"name": "tor", "type": "string"},
        {"name": "vpn", "type": "string"},
        {"name": "range", "type": "string"},
    ]
}
