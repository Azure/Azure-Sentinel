# AzureDevOpsAuditing

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-09-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure DevOps Audit Logs (via Codeless Connector Platform)](../connectors/azuredevopsauditlogs.md)

**Publisher:** Microsoft

The Azure DevOps Audit Logs data connector allows you to ingest audit events from Azure DevOps into Microsoft Sentinel. This data connector is built using the Microsoft Sentinel Codeless Connector Platform, ensuring seamless integration. It leverages the Azure DevOps Audit Logs API to fetch detailed audit events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview). These transformations enable parsing of the received audit data into a custom table during ingestion, improving query performance by eliminating the need for additional parsing. By using this connector, you can gain enhanced visibility into your Azure DevOps environment and streamline your security operations.

| | |
|--------------------------|---|
| **Tables Ingested** | `ADOAuditLogs_CL` |
| **Connector Definition Files** | [AzureDevOpsAuditLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Data%20Connectors/AzureDevOpsAuditLogs_CCP/AzureDevOpsAuditLogs_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/azuredevopsauditlogs.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ADOAuditLogs_CL` | [Azure DevOps Audit Logs (via Codeless Connector Platform)](../connectors/azuredevopsauditlogs.md) |

[← Back to Solutions Index](../solutions-index.md)
