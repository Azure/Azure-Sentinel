# SlashNext

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SlashNext |
| **Support Tier** | Partner |
| **Support Link** | [https://support@slashnext.com](https://support@slashnext.com) |
| **Categories** | domains |
| **First Published** | 2022-08-12 |
| **Last Updated** | 2022-08-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SlashNext Function App](../connectors/slashnextfunctionapp.md)

**Publisher:** SlashNext

The SlashNext function app utilizes python to perform the analysis of the raw logs and returns URLs present in the logs.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `AzureDiagnostics` |
| | `AzureMetrics` |
| **Connector Definition Files** | [SlashNext_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext/Data%20Connectors/SlashNext_FunctionApp.json) |

[→ View full connector details](../connectors/slashnextfunctionapp.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [SlashNext Function App](../connectors/slashnextfunctionapp.md) |
| `AzureMetrics` | [SlashNext Function App](../connectors/slashnextfunctionapp.md) |

[← Back to Solutions Index](../solutions-index.md)
