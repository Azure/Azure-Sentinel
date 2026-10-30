# =============================================================================
# Data Sources
# =============================================================================

# Data source to get the existing resource group
data "azurerm_resource_group" "sentinel_rg" {
  name = local.resource_group_name
}

# Data source to get the Log Analytics workspace
data "azurerm_log_analytics_workspace" "sentinel" {
  name                = local.workspace_name
  resource_group_name = local.resource_group_name
}

# Data source to get the Key Vault
data "azurerm_key_vault" "secrets" {
  name                = var.key_vault_name
  resource_group_name = var.key_vault_resource_group != "" ? var.key_vault_resource_group : local.resource_group_name
}

# Data source to get the existing Workday Data Collection Endpoint (shared with workday connector)
data "azurerm_monitor_data_collection_endpoint" "workday_dce" {
  name                = local.dce_name
  resource_group_name = local.resource_group_name
}

# Fetch Workday Email Client ID from Key Vault for each connector
data "azurerm_key_vault_secret" "client_id" {
  for_each     = var.connectors
  name         = each.value.client_id_secret_name
  key_vault_id = data.azurerm_key_vault.secrets.id
}

# Fetch Workday Email Client Secret from Key Vault for each connector
data "azurerm_key_vault_secret" "client_secret" {
  for_each     = var.connectors
  name         = each.value.client_secret_secret_name
  key_vault_id = data.azurerm_key_vault.secrets.id
}
