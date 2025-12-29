# Microsoft Exchange Security - Exchange Online

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-12-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Exchange Security Insights Online Collector](../connectors/esi-exchangeonlinecollector.md)

**Publisher:** Microsoft

Connector used to push Exchange Online Security configuration for Microsoft Sentinel Analysis

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ESIExchangeOnlineConfig_CL` |
| **Connector Definition Files** | [ESI-ExchangeOnlineCollector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Data%20Connectors/ESI-ExchangeOnlineCollector.json) |

[→ View full connector details](../connectors/esi-exchangeonlinecollector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ESIExchangeOnlineConfig_CL` | [Exchange Security Insights Online Collector](../connectors/esi-exchangeonlinecollector.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.7       | 26-03-2025                     | Update documentation link to new repository     |
| 3.1.6       | 30-08-2024                     | Correct bug on LasdtReceivedData of DataConnector. and change parser     |
| 3.1.5       | 15-05-2024                     | Enhancement in existing **Parser**       |
| 3.1.4       | 30-04-2024                     | Repackaged for parser issue       |
| 3.1.3       | 25-04-2024                     | Repackaged for parser issue with old names       |
| 3.1.2       | 18-04-2024                     | Repackaged for parser issue while update       |
| 3.1.1       | 19-03-2024                     | Manually updated package content       |
| 3.0.5       | 20-02-2024                     | Correct DataConnector last Log indicator       |
| 3.0.4       | 18-12-2023                     | Correct Parser parameters and force version update       |
| 3.0.3       | 05-12-2023                     | Added parameters in **Parser** to fix default values issue.        |
| 3.0.2       | 01-11-2023                     | Added a **Parser** to verify if user is Microsoft Exchange Security VIP (Watchlist)          |
| 3.0.1       | 13-09-2023                     | Readme file for parsers added and typo correction                      |
| 3.0.0       | 23-08-2023                     | ExchangeEnvironmentList parser name  corrected in **Workbooks**.  |

[← Back to Solutions Index](../solutions-index.md)
