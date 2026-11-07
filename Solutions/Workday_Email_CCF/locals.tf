# =============================================================================
# Local Values
# =============================================================================

locals {
  # Format location with hyphens for resource names (same as infrastructure)
  formatted_location = replace(
    replace(
      replace(
        replace(var.location, "francecentral", "france-central"),
        "eastus", "east-us"
      ),
      "northeurope", "north-europe"
    ),
    "westeurope", "west-europe"
  )

  # Compute resource names if not provided (must match infrastructure naming)
  computed_workspace_name = "${var.prefix}-${var.environment}-${local.formatted_location}"
  computed_resource_group = "${var.prefix}-rg-${var.environment}-${local.formatted_location}"

  # Use provided values or fall back to computed
  workspace_name      = var.workspace != "" ? var.workspace : local.computed_workspace_name
  resource_group_name = var.resource_group_name != "" ? var.resource_group_name : local.computed_resource_group

  existing_dce_resource_id = var.existing_data_collection_endpoint_resource_id != "" ? var.existing_data_collection_endpoint_resource_id : (
    var.data_collection_endpoint_name != "" ? "/subscriptions/${var.subscription_id}/resourceGroups/${local.resource_group_name}/providers/Microsoft.Insights/dataCollectionEndpoints/${var.data_collection_endpoint_name}" : ""
  )

  # Use location from the actual workspace (DCR must be in same region as workspace)
  actual_workspace_location = data.azurerm_log_analytics_workspace.sentinel.location
}
