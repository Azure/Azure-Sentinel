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
    "diligence_historical_statistics_url": "/ratings/v1/companies/{}/diligence/historical-statistics",
    "graph_data_url": "/ratings/v1/companies/{}/graph_data",
    "alerts_data_url": "/v2/alerts/",
}
VULNERABILITIES_URL = (
    "https://service.bitsighttech.com/customer-api/v1/defaults/vulnerabilities"
)
PORTFOLIO_PAGE_SIZE = 500
FINDINGS_PAGE_SIZE = 1000
ALERTS_PAGE_SIZE = 1000
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
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
DILIGENCE_STATISTICS_TYPE = "diligence_statistics"
INDUSTRIES_STATISTICS_TYPE = "industries_statistics"
OBSERVATIONS_STATISTICS_TYPE = "observations_statistics"
DILIGENCE_HISTORICAL_STATISTICS_TYPE = "diligence_historical_statistics"
GRAPH_DATA_TYPE = "graph_data"
ALERTS_DATA_TYPE = "alerts_data"
DILIGENCE_STATISTICS_TABLE = os.environ.get("Diligence_Statistics_Table_Name")
INDUSTRIES_STATISTICS_TABLE = os.environ.get("Industrial_Statistics_Table_Name")
OBSERVATIONS_STATISTICS_TABLE = os.environ.get("Observation_Statistics_Table_Name")
DILIGENCE_HISTORICAL_STATISTICS_TABLE = os.environ.get(
    "Diligence_Historical_Statistics_Table_Name"
)
GRAPH_DATA_TABLE = os.environ.get("Graph_Table_Name")
ALERTS_DATA_TABLE = os.environ.get("Alerts_Table_Name")
AZURE_DATA_COLLECTION_ENDPOINT = os.environ["AZURE_DATA_COLLECTION_ENDPOINT"]
AZURE_DATA_COLLECTION_RULE_ID_COMPANY_TABLES = os.environ["AZURE_DATA_COLLECTION_RULE_ID_COMPANY_TABLES"]
AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES = os.environ["AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES"]
TABLE_NAME_RULE_ID_MAPPING = {
    COMPANIES_TABLE_NAME: AZURE_DATA_COLLECTION_RULE_ID_COMPANY_TABLES,
    COMPANY_DETAIL_TABLE_NAME: AZURE_DATA_COLLECTION_RULE_ID_COMPANY_TABLES,
    COMPANIES_RATING_DETAILS_TABLE_NAME: AZURE_DATA_COLLECTION_RULE_ID_COMPANY_TABLES,
    BREACHES_TABLE_NAME: AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES,
    FINDINGS_SUMMARY_TABLE_NAME: AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES,
    FINDINGS_TABLE_NAME: AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES,
    DILIGENCE_STATISTICS_TABLE: AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES,
    INDUSTRIES_STATISTICS_TABLE: AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES,
    OBSERVATIONS_STATISTICS_TABLE: AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES,
    DILIGENCE_HISTORICAL_STATISTICS_TABLE: AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES,
    GRAPH_DATA_TABLE: AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES,
    ALERTS_DATA_TABLE: AZURE_DATA_COLLECTION_RULE_ID_DATA_TABLES,
}
SCOPE = os.environ["SCOPE"]
LOGS_STARTS_WITH = "BitSight:"
BREACHES_FUNC_NAME = "Breaches:"
FINDINGS_SUMMARY_FUNC_NAME = "Findings Summary:"
FINDINGS_FUNC_NAME = "Findings:"
COMPANY_DETAILS_FUNC_NAME = "Company Details:"
ALERT_GRAPH_STATISTICS_FUNC_NAME = "Alerts-Graph-statistics Details:"
PORTFOLIO_COMPANY_QUERY = """{}_CL
    | summarize arg_max(TimeGenerated, *) by guid
    | sort by name asc
    | project name, guid""".format(
        COMPANIES_TABLE_NAME
    )
ALERTS_DATA_CHECKPOINT_TABLE = "BitSightAlertsCheckpoint"
GRAPH_DATA_CHECKPOINT_TABLE = "BitSightGraphCheckpoint"
DILIGENCE_HISTORICAL_STATISTICS_CHECKPOINT_TABLE = "BitSightDiligenceHistoricalStatisticsCheckpoint"
DILIGENCE_STATISTICS_CHECKPOINT_TABLE = "BitSightDiligenceStatisticsCheckpoint"
INDUSTRIES_STATISTICS_CHECKPOINT_TABLE = "BitSightIndustriesStatisticsCheckpoint"
OBSERVATIONS_STATISTICS_CHECKPOINT_TABLE = "BitSightObservationsStatisticsCheckpoint"
BREACHES_CHECKPOINT_TABLE = "BitSightBreachesCheckpoint"
FINDINGS_SUMMARY_CHECKPOINT_TABLE = "BitSightFindingsSummaryCheckpoint"
FINDINGS_CHECKPOINT_TABLE = "BitSightFindingsCheckpoint"
COMPANIES_CHECKPOINT_TABLE = "BitSightCompaniesCheckpoint"
PORTFOLIO_COMPANY_CHECKPOINT_TABLE = "BitSightPortfolioCompanyCheckpoint"
COMPANY_CHECKPOINT_PARTITION_KEY = "company"
DATA_CHECKPOINT_PARTITION_KEY = "data"
RATING_CHECKPOINT_PARTITION_KEY = "rating"
COMPANY_CHECKPOINT_ROW_KEY = "company"
RETRY_COUNT = 3
RETRY_AFTER = 29
FUNCTION_APP_TIMEOUT_SECONDS = 540
