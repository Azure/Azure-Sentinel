# Azure Logic Apps

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Logic%20Apps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Logic%20Apps) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Logic Apps](../connectors/azurelogicapps-ccp.md)

**Publisher:** Microsoft

Azure Logic Apps is a cloud-based platform for creating and running automated workflows that integrate your apps, data, services, and systems. This connector lets you stream your Azure Logic Apps diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. 

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureLogicApps_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Logic%20Apps/Data%20Connectors/AzureLogicApps_CCP.JSON) |

[→ View full connector details](../connectors/azurelogicapps-ccp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Logic Apps](../connectors/azurelogicapps-ccp.md) |

[← Back to Solutions Index](../solutions-index.md)
