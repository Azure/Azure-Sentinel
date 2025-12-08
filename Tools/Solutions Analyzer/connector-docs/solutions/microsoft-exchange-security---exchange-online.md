# Microsoft Exchange Security - Exchange Online

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `ESIExchangeOnlineConfig_CL` |
| **Connector Definition Files** | [ESI-ExchangeOnlineCollector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Data%20Connectors/ESI-ExchangeOnlineCollector.json) |

[→ View full connector details](../connectors/esi-exchangeonlinecollector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ESIExchangeOnlineConfig_CL` | [Exchange Security Insights Online Collector](../connectors/esi-exchangeonlinecollector.md) |

[← Back to Solutions Index](../solutions-index.md)
