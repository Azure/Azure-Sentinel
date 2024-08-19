import os

__all__ = [
    'RESOURCE_ID', 'IPINFO_TOKEN', 'TENANT_ID', 'CLIENT_ID', 'CLIENT_SECRET',
    'LOCATION', 'SUBCRIPTION_ID', 'RESOURCE_GROUP_NAME', 'WORKSPACE_NAME', 
    'RETENTION_IN_DAYS', 'TOTAL_RETENTION_IN_DAYS', 'DATA_COLLECTION_ENDPOINT_NAME', 
    'RIRWHOIS_DCR_NAME', 'RIRWHOIS_TABLE_NAME', 'RIRWHOIS_STREAM_DECLARATION', 
    'AZURE_SCOPE', 'AZURE_BASE_URL', 'IPINFO_BASE_URL', 'CSV_NAME', 
    'RIRWHOIS_TABLE_SCHEMA', 'RIRWHOIS_TABLE_COLUMNS'
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
RIRWHOIS_DCR_NAME = "ipinfo_rule_for_RIRWHOIS_tables"
RIRWHOIS_TABLE_NAME = "Ipinfo_RIRWHOIS_CL"
RIRWHOIS_STREAM_DECLARATION = "Custom-Ipinfo_RIRWHOIS_CL"

AZURE_SCOPE = "https://management.azure.com/.default"
AZURE_BASE_URL = f"https://management.azure.com/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft."
IPINFO_BASE_URL = "https://ipinfo.io/data"
CSV_NAME = "rir.csv.gz"

RIRWHOIS_TABLE_SCHEMA = {
    "properties": {
        "totalRetentionInDays": TOTAL_RETENTION_IN_DAYS,
        "archiveRetentionInDays": 0,
        "plan": "Analytics",
        "retentionInDaysAsDefault": True,
        "totalRetentionInDaysAsDefault": True,
        "schema": {
            "tableSubType": "DataCollectionRuleBased",
            "name": RIRWHOIS_TABLE_NAME,
            "tableType": "CustomLog",
            "description": "Range based table",
            "columns": [
                {"name": "TimeGenerated", "type": "datetime", "isDefaultDisplay": False, "isHidden": False},
                {"name": "ip_range", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "whois_id", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "name", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "country", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "status", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "tech", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "maintainer", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "admin", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "source", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "whois_domain", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "updated", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "org", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "rdns_domain", "type": "string", "isDefaultDisplay": False, "isHidden": False},
				{"name": "domain", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "geoloc", "type": "string", "isDefaultDisplay": False, "isHidden": False},
				{"name": "org_address", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "asn", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "as_name", "type": "string", "isDefaultDisplay": False, "isHidden": False},
				{"name": "as_domain", "type": "string", "isDefaultDisplay": False, "isHidden": False},
                {"name": "as_type", "type": "string", "isDefaultDisplay": False, "isHidden": False},
            ],
            "standardColumns": [{"name": "TenantId", "type": "guid", "isDefaultDisplay": False, "isHidden": False}],
            "solutions": ["LogManagement"],
            "isTroubleshootingAllowed": True,
        },
        "provisioningState": "Succeeded",
        "retentionInDays": RETENTION_IN_DAYS,
    },
    "id": f"/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.OperationalInsights/workspaces/{WORKSPACE_NAME}/tables/{RIRWHOIS_TABLE_NAME}",
    "name": RIRWHOIS_TABLE_NAME,
}

RIRWHOIS_TABLE_COLUMNS = {
    "columns": [
        {"name": "TimeGenerated", "type": "datetime"},
        {"name": "range", "type": "string"},
        {"name": "whois_id", "type": "string"},
        {"name": "name", "type": "string"},
        {"name": "country", "type": "string"},
        {"name": "status", "type": "string"},
        {"name": "tech", "type": "string"},
        {"name": "maintainer", "type": "string"},
        {"name": "admin", "type": "string"},
        {"name": "source", "type": "string"},
        {"name": "whois_domain", "type": "string"},
        {"name": "updated", "type": "string"},
        {"name": "org", "type": "string"},
        {"name": "rdns_domain", "type": "string"},
        {"name": "domain", "type": "string"},
		{"name": "geoloc", "type": "string"},
        {"name": "org_address", "type": "string"},
        {"name": "asn", "type": "string"},
        {"name": "as_name", "type": "string"},
        {"name": "as_domain", "type": "string"},
        {"name": "as_type", "type": "string"},
    ]
}
