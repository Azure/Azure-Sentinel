# Ivanti Unified Endpoint Management

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Ivanti_UEM_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ivanti%20Unified%20Endpoint%20Management/Data%20Connectors/Ivanti_UEM_Syslog.json) |

[→ View full connector details](../connectors/ivantiuem.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Ivanti Unified Endpoint Management](../connectors/ivantiuem.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 27-12-2024                     | Removed Deprecated **Data Connectors**      |
| 3.0.0       | 24-07-2024                     | Deprecated Data Connectors                  |

[← Back to Solutions Index](../solutions-index.md)
