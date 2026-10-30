# Nonprod environment configuration
environment    = "nonprod"
prefix         = "sentinel"
location_short = "ne"

# location, workspace, and resource_group_name are computed dynamically from
# environment + location passed via -var="location=..." from the pipeline

tags = {
  Environment = "nonprod"
  Project     = "azure-sentinel"
  Connector   = "Workday-Email"
}

# Key Vault Configuration
key_vault_name           = "kv-SOCINFRAP-preprod-001"
key_vault_resource_group = "rg-socinfra-preprod-001"

# Workday Email Connector Instances
connectors = {
  "workday-email" = {
    instance_name                  = "WorkdayEmail"
    token_endpoint                 = "https://services1.myworkday.com/ccx/oauth2/{tenantName}/token"
    authorization_endpoint         = "https://www.myworkday.com/{tenantName}/authorize"
    api_endpoint                   = "https://services1.myworkday.com/ccx/service/customreport2/{tenantName}/ISU_MS_Sentinel/CR_Sentinel_Email_ID_Change"
    client_id_secret_name          = "workday-client-id"
    client_secret_secret_name      = "workday-client-secret"
    query_window_in_min            = 5
  }
}
