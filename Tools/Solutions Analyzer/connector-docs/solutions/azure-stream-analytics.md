# Azure Stream Analytics

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Stream%20Analytics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Stream%20Analytics) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Stream Analytics](../connectors/azurestreamanalytics-ccp.md)

**Publisher:** Microsoft

Azure Stream Analytics is a real-time analytics and complex event-processing engine that is designed to analyze and process high volumes of fast streaming data from multiple sources simultaneously. This connector lets you stream your Azure Stream Analytics hub diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. 

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureStreamAnalytics_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Stream%20Analytics/Data%20Connectors/AzureStreamAnalytics_CCP.JSON) |

[→ View full connector details](../connectors/azurestreamanalytics-ccp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Stream Analytics](../connectors/azurestreamanalytics-ccp.md) |

[← Back to Solutions Index](../solutions-index.md)
