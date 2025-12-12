# Azure DevOps Audit Logs (via Codeless Connector Platform)

| | |
|----------|-------|
| **Connector ID** | `AzureDevOpsAuditLogs` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ADOAuditLogs_CL`](../tables-index.md#adoauditlogs_cl) |
| **Used in Solutions** | [AzureDevOpsAuditing](../solutions/azuredevopsauditing.md) |
| **Connector Definition Files** | [AzureDevOpsAuditLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Data%20Connectors/AzureDevOpsAuditLogs_CCP/AzureDevOpsAuditLogs_DataConnectorDefinition.json) |

The Azure DevOps Audit Logs data connector allows you to ingest audit events from Azure DevOps into Microsoft Sentinel. This data connector is built using the Microsoft Sentinel Codeless Connector Platform, ensuring seamless integration. It leverages the Azure DevOps Audit Logs API to fetch detailed audit events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview). These transformations enable parsing of the received audit data into a custom table during ingestion, improving query performance by eliminating the need for additional parsing. By using this connector, you can gain enhanced visibility into your Azure DevOps environment and streamline your security operations.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required.

**Custom Permissions:**
- **Azure DevOps Prerequisite**: Please ensure the following:<br> 1. Register an Entra App in Microsoft Entra Admin Center under App Registrations.<br> 2.  In 'API permissions' -  add Permissions to 'Azure DevOps - vso.auditlog'.<br> 3.  In 'Certificates & secrets' - generate 'Client secret'.<br> 4.  In 'Authentication' - add Redirect URI: 'https://portal.azure.com/TokenAuthorize/ExtensionName/Microsoft_Azure_Security_Insights'.<br> 5. In the Azure DevOps settings - enable audit log and set **View audit log** for the user. [Azure DevOps Auditing](https://learn.microsoft.com/en-us/azure/devops/organizations/audit/azure-devops-auditing?view=azure-devops&tabs=preview-page).<br> 6. Ensure the user assigned to connect the data connector has the View audit logs permission explicitly set to Allow at all times. This permission is essential for successful log ingestion. If the permission is revoked or not granted, data ingestion will fail or be interrupted.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to Azure DevOps to start collecting Audit logs in Microsoft Sentinel.**

1. Enter the App you have registered.
 2. In the 'Overview' section, copy the Application (client) ID.
 3. Select the 'Endpoints' button, and copy the 'OAuth 2.0 authorization endpoint (v2)' value and the 'OAuth 2.0 token endpoint (v2)' value.
 4. In the 'Certificates & secrets' section, copy the 'Client Secret value', and store it securely.
5. Provide the required information below and click 'Connect'.
- **Token Endpoint**: https://login.microsoftonline.com/{TenantId}/oauth2/v2.0/token
- **Authorization Endpoint**: https://login.microsoftonline.com/{TenantId}/oauth2/v2.0/authorize
- **API Endpoint**: https://auditservice.dev.azure.com/{organizationName}/_apis/audit/auditlog?api-version=7.2-preview
- **OAuth Configuration**:
  - App Client ID
  - App Client Secret
  - Click 'Connect' to authenticate

[← Back to Connectors Index](../connectors-index.md)
