variable "location" {
  description = "Azure region for deployment"
  type        = string
  default     = "francecentral"
}

variable "location_short" {
  description = "Short code for the Azure region (e.g., ne for northeurope, eu for eastus)"
  type        = string
  default     = "ne"
}

variable "environment" {
  description = "Environment name (e.g., poc, nonprod, prod)"
  type        = string
  default     = "poc"
}

variable "prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "sentinel"
}

variable "workspace" {
  description = "Workspace name for Log Analytics where Microsoft Sentinel is setup. If empty, computed from location and environment."
  type        = string
  default     = ""
}

variable "resource_group_name" {
  description = "Resource group name where Microsoft Sentinel is setup. If empty, computed from location and environment."
  type        = string
  default     = ""
}

variable "subscription_id" {
  description = "Subscription ID where Microsoft Sentinel is setup"
  type        = string
}

variable "connectors" {
  description = "Map of Workday Email Activity connector instances to deploy"
  type = map(object({
    instance_name                    = string
    token_endpoint                   = string
    authorization_endpoint           = string
    api_endpoint                     = string
    client_id_secret_name            = string
    client_secret_secret_name        = string
    query_window_in_min              = optional(number, 5)
  }))

  validation {
    condition = alltrue([
      for k, v in var.connectors : length(v.instance_name) >= 1 && length(v.instance_name) <= 20
    ])
    error_message = "Each connector instance_name must be between 1 and 20 characters long."
  }
}

variable "tags" {
  description = "Tags to apply to deployed resources"
  type        = map(string)
  default     = {}
}

# Key Vault configuration for secrets
variable "key_vault_name" {
  description = "Name of the Azure Key Vault containing Workday Email secrets"
  type        = string
}

variable "key_vault_resource_group" {
  description = "Resource group of the Azure Key Vault. If not specified, uses the same resource group as the deployment."
  type        = string
  default     = ""
}

# Data Collection configuration
variable "create_data_collection_resources" {
  description = "Whether to create DCE and DCR resources. Set to false if they already exist."
  type        = bool
  default     = true
}

variable "deploy_connections" {
  description = "Whether to deploy the Workday Email data connector pollers (RestApiPoller resources). Set to true to deploy connections with credentials from Key Vault."
  type        = bool
  default     = false
}

variable "data_collection_endpoint_name" {
  description = "Name of the existing Data Collection Endpoint (shared with workday connector). If not specified, defaults to dce-workday-{env}-{location}."
  type        = string
  default     = ""
}

variable "data_collection_rule_name" {
  description = "Name of the Data Collection Rule. If not specified, defaults to dcr-workday-email-{env}-{location}."
  type        = string
  default     = ""
}
