# Doppel Data Connector

| | |
|----------|-------|
| **Connector ID** | `Doppel_DataConnector` |
| **Publisher** | Doppel |
| **Tables Ingested** | [`DoppelTable_CL`](../tables-index.md#doppeltable_cl) |
| **Used in Solutions** | [Doppel](../solutions/doppel.md) |
| **Connector Definition Files** | [Template_Doppel.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Doppel/Data%20Connectors/Template_Doppel.json) |

The data connector is built on Microsoft Sentinel for Doppel events and alerts and supports DCR-based [ingestion time transformations](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/ingestion-time-transformations) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

[← Back to Connectors Index](../connectors-index.md)
