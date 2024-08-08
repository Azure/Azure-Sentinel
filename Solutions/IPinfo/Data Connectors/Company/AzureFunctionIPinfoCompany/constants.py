import os

__all__ = [
    'RESOURCE_ID', 'IPINFO_TOKEN', 'TENANT_ID', 'CLIENT_ID', 'CLIENT_SECRET',
    'LOCATION', 'SUBCRIPTION_ID', 'RESOURCE_GROUP_NAME',
    'WORKSPACE_NAME', 'RETENTION_IN_DAYS', 'TOTAL_RETENTION_IN_DAYS',
    'DATA_COLLECTION_ENDPOINT_NAME', 'COMPANY_DCR_NAME', 'COMPANY_TABLE_NAME',
    'COMPANY_STREAM_DECLARATION', 'AZURE_SCOPE', 'AZURE_BASE_URL', 'IPINFO_BASE_URL',
    'MMDB_NAME', 'COMPANY_TABLE_SCHEMA', 'COMPANY_TABLE_COLUMNS'
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
COMPANY_DCR_NAME = "ipinfo_rule_for_company_table"
COMPANY_TABLE_NAME = "Ipinfo_Company_CL"
COMPANY_STREAM_DECLARATION = "Custom-Ipinfo_Company_CL"

AZURE_SCOPE = "https://management.azure.com/.default"
AZURE_BASE_URL = f"https://management.azure.com/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft."
IPINFO_BASE_URL = "https://ipinfo.io/data"
MMDB_NAME = "standard_company.mmdb"

COMPANY_TABLE_SCHEMA = {
    "properties": {
        "totalRetentionInDays": TOTAL_RETENTION_IN_DAYS,
        "archiveRetentionInDays": 0,
        "plan": "Analytics",
        "retentionInDaysAsDefault": True,
        "totalRetentionInDaysAsDefault": True,
        "schema": {
            "tableSubType": "DataCollectionRuleBased",
            "name": COMPANY_TABLE_NAME,
            "tableType": "CustomLog",
            "description": "Range based table",
            "columns": [
                {"name": "as_domain", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "as_name", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "as_type", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "asn", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "country", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "company_domain", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "company_name", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "company_type", "type": "string", "isDefaultDisplay": False, "isHidden": False},
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
    "id": f"/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.OperationalInsights/workspaces/{WORKSPACE_NAME}/tables/{COMPANY_TABLE_NAME}",
    "name": COMPANY_TABLE_NAME,
}

COMPANY_TABLE_COLUMNS = {
    "columns": [
        {"name": "TimeGenerated", "type": "datetime"},
        {"name": "as_domain", "type": "string"},
        {"name": "as_name", "type": "string"},
        {"name": "as_type", "type": "string"},
        {"name": "asn", "type": "string"},
        {"name": "country", "type": "string"},
        {"name": "company_domain", "type": "string"},
        {"name": "company_name", "type": "string"},
        {"name": "company_type", "type": "string"},
        {"name": "range", "type": "string"},
    ]
}
