resource "azurerm_resource_group_template_deployment" "workday_email_solution" {
  name                = "workday-email-solution-deployment"
  resource_group_name = data.azurerm_resource_group.sentinel_rg.name
  deployment_mode     = "Incremental"
  template_content    = file("${path.module}/PollerConnector.json")

  parameters_content = jsonencode({
    workspace = {
      value = local.workspace_name
    }
    "workspace-location" = {
      value = local.actual_workspace_location
    }
    existingDataCollectionEndpointResourceId = {
      value = local.existing_dce_resource_id
    }
    dataCollectionRuleName = {
      value = var.data_collection_rule_name
    }
  })

  tags = var.tags

  lifecycle {
    precondition {
      condition     = var.data_collection_endpoint_name == "" || var.existing_data_collection_endpoint_resource_id == ""
      error_message = "Specify either data_collection_endpoint_name or existing_data_collection_endpoint_resource_id, not both."
    }
  }
}
