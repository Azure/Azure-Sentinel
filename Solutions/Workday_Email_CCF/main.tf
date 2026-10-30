# =============================================================================
# Workday Email Activity Sentinel Connector - Resource Definitions
# =============================================================================
# File layout:
#   providers.tf  -> Provider configuration
#   locals.tf     -> Local values (naming, computed resource names)
#   data.tf       -> Data sources (resource group, workspace, Key Vault, secrets)
#   variables.tf  -> Input variables
#   outputs.tf    -> Output values
#   versions.tf   -> Required providers and versions
#   main.tf       -> Resource definitions (this file)
# =============================================================================

# --------------------------------------------------------------------------
# Deploy the Workday Email Solution ARM Template (PollerConnector.json)
# This registers the content package, connector definition, DCR, and
# connection templates in Microsoft Sentinel.
# --------------------------------------------------------------------------

resource "azurerm_resource_group_template_deployment" "workday_email_solution" {
  name                = "workday-email-solution-deployment"
  resource_group_name = data.azurerm_resource_group.sentinel_rg.name
  deployment_mode     = "Incremental"
  template_content    = file("${path.module}/PollerConnector.json")

  parameters_content = jsonencode({
    "workspace" = {
      value = local.workspace_name
    }
  })

  tags = var.tags

  lifecycle {
    ignore_changes = [template_content]
  }
}

# --------------------------------------------------------------------------
# Data Collection Rule for Workday Email Activity
# Maps raw Workday custom report fields to ASIM AuditEvent schema via KQL
# --------------------------------------------------------------------------

resource "azurerm_monitor_data_collection_rule" "workday_email" {
  for_each            = var.create_data_collection_resources ? var.connectors : {}
  name                = "${local.dcr_name}"
  resource_group_name = data.azurerm_resource_group.sentinel_rg.name
  location            = local.actual_workspace_location
  description         = "Data Collection Rule for Workday Email Activity ${each.value.instance_name} Connector"

  tags = merge(var.tags, {
    createdBy = "Sentinel"
  })

  data_collection_endpoint_id = data.azurerm_monitor_data_collection_endpoint.workday_dce.id

  # Declare the incoming custom stream with Workday Email Activity report columns
  stream_declaration {
    stream_name = "Custom-ASimAuditEventLogs"
    column {
      name = "DateTimeStamp"
      type = "string"
    }
    column {
      name = "EmailIDAfter"
      type = "string"
    }
    column {
      name = "EmailIDBefore"
      type = "string"
    }
    column {
      name = "Employee_ID"
      type = "string"
    }
    column {
      name = "Login_ID"
      type = "string"
    }
    column {
      name = "TargetID"
      type = "string"
    }
    column {
      name = "Worker"
      type = "string"
    }
  }

  destinations {
    log_analytics {
      workspace_resource_id = data.azurerm_log_analytics_workspace.sentinel.id
      name                  = "clv2ws1"
    }
  }

  data_flow {
    streams       = ["Custom-ASimAuditEventLogs"]
    destinations  = ["clv2ws1"]
    transform_kql = <<-KQL
      source
      | extend TimeGenerated = todatetime(DateTimeStamp), EventStartTime = todatetime(DateTimeStamp), EventEndTime = todatetime(DateTimeStamp)
      | project-rename OldValue = EmailIDBefore, NewValue = EmailIDAfter, ActorUserId = Employee_ID, ActorUsername = Login_ID, EventOriginalUid = TargetID, Object = Worker
      | extend EventCount = toint(1), EventSchema = "AuditEvent", EventResult = "Success", EventProduct = "Workday", EventVendor = "Workday", EventSchemaVersion = "0.1", ObjectType = "Other", EventType = "Set", Operation = "Email Activity", Dvc = "Workday"
    KQL
    output_stream = "Microsoft-ASimAuditEventLogs"
  }
}

# --------------------------------------------------------------------------
# Deploy Workday Email Data Connector Pollers (RestApiPoller resources)
# These are the actual connectors that poll the Workday Custom Report API
# --------------------------------------------------------------------------

resource "azurerm_resource_group_template_deployment" "workday_email_connection" {
  for_each            = var.deploy_connections ? var.connectors : {}
  name                = "workday-email-connection-${each.key}"
  resource_group_name = data.azurerm_resource_group.sentinel_rg.name
  deployment_mode     = "Incremental"

  template_content = templatefile("${path.module}/connection-template.json", {})

  parameters_content = jsonencode({
    "workspace" = {
      value = local.workspace_name
    }
    "workspace-location" = {
      value = local.actual_workspace_location
    }
    "connectorInstanceName" = {
      value = each.value.instance_name
    }
    "tokenEndpoint" = {
      value = each.value.token_endpoint
    }
    "authorizationEndpoint" = {
      value = each.value.authorization_endpoint
    }
    "apiEndpoint" = {
      value = each.value.api_endpoint
    }
    "clientId" = {
      value = data.azurerm_key_vault_secret.client_id[each.key].value
    }
    "clientSecret" = {
      value = data.azurerm_key_vault_secret.client_secret[each.key].value
    }
    "authorizationCode" = {
      value = "-NA-"
    }
    "queryWindowInMin" = {
      value = each.value.query_window_in_min
    }
    "dataCollectionEndpoint" = {
      value = data.azurerm_monitor_data_collection_endpoint.workday_dce.logs_ingestion_endpoint
    }
    "dataCollectionRuleImmutableId" = {
      value = azurerm_monitor_data_collection_rule.workday_email[each.key].immutable_id
    }
  })

  tags = var.tags

  lifecycle {
    precondition {
      condition     = data.azurerm_key_vault_secret.client_id[each.key].value != null && data.azurerm_key_vault_secret.client_id[each.key].value != ""
      error_message = "Client ID for connector '${each.key}' is null or empty. Check Key Vault secret '${each.value.client_id_secret_name}'."
    }
    precondition {
      condition     = data.azurerm_key_vault_secret.client_secret[each.key].value != null && data.azurerm_key_vault_secret.client_secret[each.key].value != ""
      error_message = "Client Secret for connector '${each.key}' is null or empty. Check Key Vault secret '${each.value.client_secret_secret_name}'."
    }

  }

  depends_on = [
    azurerm_resource_group_template_deployment.workday_email_solution,
    azurerm_monitor_data_collection_rule.workday_email
  ]
}
