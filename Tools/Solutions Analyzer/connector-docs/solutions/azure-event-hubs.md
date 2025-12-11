# Azure Event Hubs

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Event%20Hubs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Event%20Hubs) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Event Hub](../connectors/azureeventhub-ccp.md)

**Publisher:** Microsoft

Azure Event Hubs is a big data streaming platform and event ingestion service. It can receive and process millions of events per second. This connector lets you stream your Azure Event Hub diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. 

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureEventHub_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Event%20Hubs/Data%20Connectors/AzureEventHub_CCP.JSON) |

[→ View full connector details](../connectors/azureeventhub-ccp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Event Hub](../connectors/azureeventhub-ccp.md) |

[← Back to Solutions Index](../solutions-index.md)
