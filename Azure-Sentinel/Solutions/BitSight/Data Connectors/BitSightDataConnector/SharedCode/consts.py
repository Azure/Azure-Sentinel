"""Module with constants and configurations for the BitSight integration."""
import os

API_TOKEN = os.environ.get("API_token")
AZURE_AUTHENTICATION_URL = "https://login.microsoftonline.com/{}/oauth2/token"
BASE_URL = "https://api.bitsighttech.com"
ENDPOINTS = {
    "portfolio_path": "/ratings/v2/portfolio",
    "company_endpoint_path": "/ratings/v1/companies/{}",
    "breaches_endpoint_path": "/v1/companies/{}/providers/breaches",
    "findings_summary_endpoint_path": "/ratings/v1/companies/{}/findings/summary",
    "findings_endpoint_path": "/ratings/v1/companies/{}/findings",
    "diligence_statistics_url": "/ratings/v1/companies/{}/diligence/statistics",
    "industries_statistics_url": "/ratings/v1/companies/{}/industries/statistics",
    "observations_statistics_url": "/ratings/v1/companies/{}/observations/statistics",
    "diligence_historical-statistics_url": "/ratings/v1/companies/{}/diligence/historical-statistics",
    "graph_data_url": "/ratings/v1/companies/{}/graph_data",
    "alerts_url": "/v2/alerts/",
}
VULNERABILITIES_URL = (
    "https://service.bitsighttech.com/customer-api/v1/defaults/vulnerabilities"
)
PORTFOLIO_PAGE_SIZE = 500
FINDINGS_PAGE_SIZE = 1000
ALERTS_PAGE_SIZE = 1000
AZURE_CLIENT_ID = os.environ.get("Azure_Client_Id")
AZURE_CLIENT_SECRET = os.environ.get("Azure_Client_Secret")
AZURE_TENANT_ID = os.environ.get("Azure_Tenant_Id")
CONN_STRING = os.environ.get("AzureWebJobsStorage")
COMPANIES = os.environ.get("Companies")
WORKSPACE_ID = os.environ.get("WorkspaceID")
WORKSPACE_KEY = os.environ.get("WorkspaceKey")
COMPANIES_TABLE_NAME = os.environ.get("Portfolio_Companies_Table_Name")
COMPANY_DETAIL_TABLE_NAME = os.environ.get("Company_Table_Name")
COMPANIES_RATING_DETAILS_TABLE_NAME = os.environ.get(
    "Company_Rating_Details_Table_Name"
)
BREACHES_TABLE_NAME = os.environ.get("Breaches_Table_Name")
FINDINGS_SUMMARY_TABLE_NAME = os.environ.get("Findings_Summary_Table_Name")
FINDINGS_TABLE_NAME = os.environ.get("Findings_Table_Name")
DILIGENCE_STATISCTICS_TABLE = os.environ.get("Diligence_Statistics_Table_Name")
INDUSTRIAL_STATISCTICS_TABLE = os.environ.get("Industrial_Statistics_Table_Name")
OBSERVATION_STATISCTICS_TABLE = os.environ.get("Observation_Statistics_Table_Name")
DILIGENCE_HISTORICAL_STATISTICS_TABLE = os.environ.get(
    "Diligence_Historical_Statistics_Table_Name"
)
GRAPH_DATA_TABLE = os.environ.get("Graph_Table_Name")
ALERTS_DATA_TABLE = os.environ.get("Alerts_Table_Name")
LOGS_STARTS_WITH = "BitSight:"
BREACHES_FUNC_NAME = "Breaches:"
FINDINGS_SUMMARY_FUNC_NAME = "Findings Summary:"
FINDINGS_FUNC_NAME = "Findings:"
COMPANY_DETAILS_FUNC_NAME = "Company Details:"
ALERT_GRAPH_STATISTICS_FUNC_NAME = "Alerts-Graph-statistics Details:"
