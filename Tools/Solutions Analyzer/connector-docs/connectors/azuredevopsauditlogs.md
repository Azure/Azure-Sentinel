# Azure DevOps Audit Logs (via Codeless Connector Platform)

| | |
|----------|-------|
| **Connector ID** | `AzureDevOpsAuditLogs` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ADOAuditLogs_CL`](../tables-index.md#adoauditlogs_cl) |
| **Used in Solutions** | [AzureDevOpsAuditing](../solutions/azuredevopsauditing.md) |
| **Connector Definition Files** | [AzureDevOpsAuditLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Data%20Connectors/AzureDevOpsAuditLogs_CCP/AzureDevOpsAuditLogs_DataConnectorDefinition.json) |

The Azure DevOps Audit Logs data connector allows you to ingest audit events from Azure DevOps into Microsoft Sentinel. This data connector is built using the Microsoft Sentinel Codeless Connector Platform, ensuring seamless integration. It leverages the Azure DevOps Audit Logs API to fetch detailed audit events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview). These transformations enable parsing of the received audit data into a custom table during ingestion, improving query performance by eliminating the need for additional parsing. By using this connector, you can gain enhanced visibility into your Azure DevOps environment and streamline your security operations.

[← Back to Connectors Index](../connectors-index.md)
