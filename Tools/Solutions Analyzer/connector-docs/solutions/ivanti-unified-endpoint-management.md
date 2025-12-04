# Ivanti Unified Endpoint Management

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-07-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ivanti%20Unified%20Endpoint%20Management](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ivanti%20Unified%20Endpoint%20Management) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Ivanti Unified Endpoint Management](../connectors/ivantiuem.md)

**Publisher:** Ivanti

The [Ivanti Unified Endpoint Management](https://www.ivanti.com/products/unified-endpoint-manager) data connector provides the capability to ingest [Ivanti UEM Alerts](https://help.ivanti.com/ld/help/en_US/LDMS/11.0/Windows/alert-c-monitoring-overview.htm) into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Ivanti_UEM_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ivanti%20Unified%20Endpoint%20Management/Data%20Connectors/Ivanti_UEM_Syslog.json) |

[→ View full connector details](../connectors/ivantiuem.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Ivanti Unified Endpoint Management](../connectors/ivantiuem.md) |

[← Back to Solutions Index](../solutions-index.md)
