variable "location" {
  description = "Region used to compute workspace and resource group names. The actual workspace region is used for ARM deployment."
  type        = string
  default     = "francecentral"
}

variable "location_short" {
  description = "Legacy location short code, retained for compatibility with environment files."
  type        = string
  default     = "ne"
}

variable "environment" {
  description = "Environment name used to compute resource names."
  type        = string
  default     = "poc"
}

variable "prefix" {
  description = "Prefix for computed workspace and resource group names."
  type        = string
  default     = "sentinel"
}

variable "workspace" {
  description = "Existing Sentinel workspace name. If empty, computed from prefix, environment, and location."
  type        = string
  default     = ""
}

variable "resource_group_name" {
  description = "Existing workspace resource group. If empty, computed from prefix, environment, and location."
  type        = string
  default     = ""
}

variable "subscription_id" {
  description = "Subscription containing the existing Microsoft Sentinel workspace."
  type        = string
}

variable "tags" {
  description = "Tags for the ARM deployment."
  type        = map(string)
  default     = {}
}

variable "existing_data_collection_endpoint_resource_id" {
  description = "Optional existing DCE resource ID in the workspace region. Empty creates a dedicated DCE."
  type        = string
  default     = ""
}

variable "data_collection_endpoint_name" {
  description = "Optional existing DCE name in the workspace resource group. Do not combine with an explicit DCE resource ID."
  type        = string
  default     = ""
}

variable "data_collection_rule_name" {
  description = "Optional dedicated DCR name created by Sentinel during portal connection, not by Terraform."
  type        = string
  default     = ""
}
