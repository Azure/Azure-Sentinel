# POC environment configuration
environment    = "poc"
prefix         = "sentinel"
location_short = "ne"

# location, workspace, and resource_group_name are computed dynamically from
# environment + location passed via -var="location=..." from the pipeline

tags = {
  Environment = "poc"
  Project     = "azure-sentinel"
  Connector   = "Workday-Email"
}

# Key Vault Configuration - Use DEV Key Vault
key_vault_name           = "kv-SOCINFRAD-dev-001"
key_vault_resource_group = "rg-socinfra-dev-001"

# Deploy the actual data connector pollers with credentials from Key Vault
deploy_connections = true

# Workday Email Connector Instances
connectors = {
  "workday-email" = {
    instance_name                  = "WorkdayEmail"
    token_endpoint                 = "https://wd3-impl-services1.workday.com/ccx/oauth2/{tenantName}/token"
    authorization_endpoint         = "https://impl.workday.com/{tenantName}/authorize"
    api_endpoint                   = "https://wd3-impl-services1.workday.com/ccx/service/customreport2/{tenantName}/ISU_MS_Sentinel/CR_Sentinel_Email_ID_Change"
    client_id_secret_name          = "workday-client-id"
    client_secret_secret_name      = "workday-client-secret"
    query_window_in_min            = 5
  }
}
