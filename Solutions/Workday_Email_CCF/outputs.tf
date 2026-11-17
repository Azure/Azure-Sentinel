output "solution_deployment_id" {
  description = "ID of the connector installer ARM deployment."
  value       = azurerm_resource_group_template_deployment.workday_email_solution.id
}

output "solution_deployment_name" {
  description = "Name of the connector installer ARM deployment."
  value       = azurerm_resource_group_template_deployment.workday_email_solution.name
}

output "connector_definition_name" {
  description = "Installed connector definition. This does not indicate OAuth connection or ingestion success."
  value       = jsondecode(azurerm_resource_group_template_deployment.workday_email_solution.output_content).connectorDefinitionName.value
}

output "data_collection_endpoint_id" {
  description = "DCE resource ID selected by the installer."
  value       = jsondecode(azurerm_resource_group_template_deployment.workday_email_solution.output_content).dataCollectionEndpointResourceId.value
}

output "data_collection_rule_name" {
  description = "DCR name reserved for portal connection. The installer does not create the DCR."
  value       = jsondecode(azurerm_resource_group_template_deployment.workday_email_solution.output_content).dataCollectionRuleName.value
}

output "next_step" {
  description = "Required interactive OAuth connection step."
  value       = jsondecode(azurerm_resource_group_template_deployment.workday_email_solution.output_content).nextStep.value
}
