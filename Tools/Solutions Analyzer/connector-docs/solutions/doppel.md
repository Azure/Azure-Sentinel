# Doppel

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Doppel |
| **Support Tier** | Partner |
| **Support Link** | [https://www.doppel.com/request-a-demo](https://www.doppel.com/request-a-demo) |
| **Categories** | domains |
| **First Published** | 2024-11-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Doppel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Doppel) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Doppel Data Connector](../connectors/doppel-dataconnector.md)

**Publisher:** Doppel

The data connector is built on Microsoft Sentinel for Doppel events and alerts and supports DCR-based [ingestion time transformations](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/ingestion-time-transformations) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

| | |
|--------------------------|---|
| **Tables Ingested** | `DoppelTable_CL` |
| **Connector Definition Files** | [Template_Doppel.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Doppel/Data%20Connectors/Template_Doppel.json) |

[→ View full connector details](../connectors/doppel-dataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DoppelTable_CL` | [Doppel Data Connector](../connectors/doppel-dataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
