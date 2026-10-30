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

  # Reference the existing Workday DCE (shared with workday connector)
  dce_name = var.data_collection_endpoint_name != "" ? var.data_collection_endpoint_name : "dce-workday-${var.environment}-${var.location_short}"
  dcr_name = var.data_collection_rule_name != "" ? var.data_collection_rule_name : "dcr-workday-email-${var.environment}-${var.location_short}"

  # Use location from the actual workspace (DCR must be in same region as workspace)
  actual_workspace_location = data.azurerm_log_analytics_workspace.sentinel.location
}
