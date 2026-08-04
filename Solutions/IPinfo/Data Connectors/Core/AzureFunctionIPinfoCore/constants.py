import os

__all__ = [
    'RESOURCE_ID', 'IPINFO_TOKEN', 'TENANT_ID', 'CLIENT_ID', 'CLIENT_SECRET',
    'LOCATION', 'SUBCRIPTION_ID', 'RESOURCE_GROUP_NAME', 'WORKSPACE_NAME', 
    'RETENTION_IN_DAYS', 'TOTAL_RETENTION_IN_DAYS', 'DATA_COLLECTION_ENDPOINT_NAME', 
    'CORE_DCR_NAME', 'CORE_TABLE_NAME', 'CORE_STREAM_DECLARATION', 
    'AZURE_SCOPE', 'AZURE_BASE_URL', 'IPINFO_BASE_URL', 'MMDB_NAME', 
    'CORE_TABLE_SCHEMA', 'CORE_TABLE_COLUMNS'
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
CORE_DCR_NAME = f"ipinfo_rule_for_CORE_tables-{WORKSPACE_NAME.lower()}"
CORE_TABLE_NAME = "Ipinfo_CORE_CL"
CORE_STREAM_DECLARATION = "Custom-Ipinfo_CORE_CL"

AZURE_SCOPE = "https://management.azure.com/.default"
AZURE_BASE_URL = f"https://management.azure.com/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft."
IPINFO_BASE_URL = "https://ipinfo.io/data"
MMDB_NAME = "ipinfo_core.mmdb"

CORE_TABLE_SCHEMA = {
    "properties": {
        "totalRetentionInDays": TOTAL_RETENTION_IN_DAYS,
        "archiveRetentionInDays": 0,
        "plan": "Analytics",
        "retentionInDaysAsDefault": True,
        "totalRetentionInDaysAsDefault": True,      
        "schema": {
            "tableSubType": "DataCollectionRuleBased",
            "name": CORE_TABLE_NAME,
            "tableType": "CustomLog",
            "description": "Range based table",
            "columns": [
                {"name": "TimeGenerated", "type": "datetime", "isDefaultDisplay": False, "isHidden": False},
                {"name": "ip_range", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "city", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "region", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "region_code", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "country", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "country_code", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "continent", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "continent_code", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "latitude", "type": "real", "isDefaultDisplay": False, "isHidden": False},
                {"name": "longitude", "type": "real", "isDefaultDisplay": False, "isHidden": False},
                {"name": "timezone", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "postal_code", "type": "string", "isDefaultDisplay": False, "isHidden": False},
				{"name": "asn", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "as_name", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "as_domain", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "as_type", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "is_anonymous", "type": "boolean", "isDefaultDisplay": False, "isHidden": False},
                {"name": "is_anycast", "type": "boolean", "isDefaultDisplay": False, "isHidden": False},
                {"name": "is_hosting", "type": "boolean", "isDefaultDisplay": False, "isHidden": False},
                {"name": "is_mobile", "type": "boolean", "isDefaultDisplay": False, "isHidden": False},
                {"name": "is_satellite", "type": "boolean", "isDefaultDisplay": False, "isHidden": False},
            ],
            "standardColumns": [{"name": "TenantId", "type": "guid", "isDefaultDisplay": False, "isHidden": False}],
            "solutions": ["LogManagement"],
            "isTroubleshootingAllowed": True,
        },
        "provisioningState": "Succeeded",
        "retentionInDays": RETENTION_IN_DAYS,
    },
    "id": f"/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.OperationalInsights/workspaces/{WORKSPACE_NAME}/tables/{CORE_TABLE_NAME}",
    "name": CORE_TABLE_NAME,
}

CORE_TABLE_COLUMNS = {
    "columns": [
        {"name": "TimeGenerated", "type": "datetime"},
        {"name": "range", "type": "string"},
        {"name": "city", "type": "string"},
        {"name": "region", "type": "string"},
        {"name": "region_code", "type": "string"},
        {"name": "country", "type": "string"},
        {"name": "country_code", "type": "string"},
        {"name": "continent", "type": "string"},
        {"name": "continent_code", "type": "string"},
        {"name": "latitude", "type": "real"},
        {"name": "longitude", "type": "real"},
        {"name": "timezone", "type": "string"},
        {"name": "postal_code", "type": "string"},
        {"name": "asn", "type": "string"},
        {"name": "as_name", "type": "string"},
        {"name": "as_domain", "type": "string"},
        {"name": "as_type", "type": "string"},
        {"name": "is_anonymous", "type": "boolean"},
        {"name": "is_anycast", "type": "boolean"},
        {"name": "is_hosting", "type": "boolean"},
        {"name": "is_mobile", "type": "boolean"},
        {"name": "is_satellite", "type": "boolean"},
    ]
}
