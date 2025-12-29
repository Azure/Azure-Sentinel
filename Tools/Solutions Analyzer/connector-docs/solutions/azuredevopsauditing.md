# AzureDevOpsAuditing

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ADOAuditLogs_CL` |
| **Connector Definition Files** | [AzureDevOpsAuditLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Data%20Connectors/AzureDevOpsAuditLogs_CCP/AzureDevOpsAuditLogs_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/azuredevopsauditlogs.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ADOAuditLogs_CL` | [Azure DevOps Audit Logs (via Codeless Connector Platform)](../connectors/azuredevopsauditlogs.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                         |
|-------------|--------------------------------|----------------------------------------------------------------------------|
| 3.0.6       | 19-06-2025                     | Updated **Data Connector** instructions to include a note about User permissions.                                   |
| 3.0.5       | 05-05-2025                     | Updated **Data Connector** instructions.                                   |
| 3.0.4       | 15-04-2025                     | Added new **CCP Connector** - Azure DevOps Audit Logs. 					   		   |
| 3.0.3       | 16-07-2024                     | Updated the **Analytic rules** for missing TTP.					   		   |
| 3.0.2       | 23-01-2024                     | Updated the solution to fix **Analytic Rules** deployment issue.            |
| 3.0.1       | 27-11-2023                     | Added new Entity Mappings to **Analytic Rules**.                            |
| 3.0.0       | 06-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.   |

[← Back to Solutions Index](../solutions-index.md)
