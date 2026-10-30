output "solution_deployment_id" {
  description = "The ID of the Workday Email solution ARM template deployment"
  value       = azurerm_resource_group_template_deployment.workday_email_solution.id
}

output "solution_deployment_name" {
  description = "The name of the Workday Email solution ARM template deployment"
  value       = azurerm_resource_group_template_deployment.workday_email_solution.name
}

output "connection_deployment_ids" {
  description = "The IDs of the Workday Email connection ARM template deployments"
  value       = { for k, v in azurerm_resource_group_template_deployment.workday_email_connection : k => v.id }
}

output "connection_deployment_names" {
  description = "The names of the Workday Email connection ARM template deployments"
  value       = { for k, v in azurerm_resource_group_template_deployment.workday_email_connection : k => v.name }
}

output "connectors_deployed" {
  description = "List of connector instance names deployed"
  value       = [for k, v in var.connectors : v.instance_name]
}

output "data_collection_endpoint_id" {
  description = "The ID of the existing Workday Data Collection Endpoint (shared)"
  value       = data.azurerm_monitor_data_collection_endpoint.workday_dce.id
}

output "data_collection_endpoint_url" {
  description = "The logs ingestion endpoint URL"
  value       = data.azurerm_monitor_data_collection_endpoint.workday_dce.logs_ingestion_endpoint
}

output "data_collection_rule_ids" {
  description = "The IDs of the Data Collection Rules"
  value       = var.create_data_collection_resources ? { for k, v in azurerm_monitor_data_collection_rule.workday_email : k => v.id } : {}
}

output "data_collection_rule_immutable_ids" {
  description = "The immutable IDs of the Data Collection Rules"
  value       = var.create_data_collection_resources ? { for k, v in azurerm_monitor_data_collection_rule.workday_email : k => v.immutable_id } : {}
}
