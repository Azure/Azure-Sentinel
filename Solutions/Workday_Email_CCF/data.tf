data "azurerm_resource_group" "sentinel_rg" {
  name = local.resource_group_name
}

data "azurerm_log_analytics_workspace" "sentinel" {
  name                = local.workspace_name
  resource_group_name = local.resource_group_name
}
