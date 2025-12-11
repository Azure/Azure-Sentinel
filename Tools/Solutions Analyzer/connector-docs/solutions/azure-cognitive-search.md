# Azure Cognitive Search

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Cognitive%20Search](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Cognitive%20Search) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Cognitive Search](../connectors/azurecognitivesearch-ccp.md)

**Publisher:** Microsoft

Azure Cognitive Search is a cloud search service that gives developers infrastructure, APIs, and tools for building a rich search experience over private, heterogeneous content in web, mobile, and enterprise applications. This connector lets you stream your Azure Cognitive Search diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. 

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureCognitiveSearch_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Cognitive%20Search/Data%20Connectors/AzureCognitiveSearch_CCP.JSON) |

[→ View full connector details](../connectors/azurecognitivesearch-ccp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Cognitive Search](../connectors/azurecognitivesearch-ccp.md) |

[← Back to Solutions Index](../solutions-index.md)
