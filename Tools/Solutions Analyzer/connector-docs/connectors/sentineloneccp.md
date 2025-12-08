# SentinelOne

| | |
|----------|-------|
| **Connector ID** | `SentinelOneCCP` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SentinelOneActivities_CL`](../tables-index.md#sentineloneactivities_cl), [`SentinelOneAgents_CL`](../tables-index.md#sentineloneagents_cl), [`SentinelOneAlerts_CL`](../tables-index.md#sentinelonealerts_cl), [`SentinelOneGroups_CL`](../tables-index.md#sentinelonegroups_cl), [`SentinelOneThreats_CL`](../tables-index.md#sentinelonethreats_cl) |
| **Used in Solutions** | [SentinelOne](../solutions/sentinelone.md) |
| **Connector Definition Files** | [connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Data%20Connectors/SentinelOne_ccp/connectorDefinition.json) |

The [SentinelOne](https://usea1-nessat.sentinelone.net/api-doc/overview) data connector allows ingesting logs from the SentinelOne API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the SentinelOne API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

[← Back to Connectors Index](../connectors-index.md)
