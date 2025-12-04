# SentinelOne

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-11-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [SentinelOne](../connectors/sentinelone.md)

**Publisher:** SentinelOne

### [SentinelOne](../connectors/sentineloneccp.md)

**Publisher:** Microsoft

The [SentinelOne](https://usea1-nessat.sentinelone.net/api-doc/overview) data connector allows ingesting logs from the SentinelOne API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the SentinelOne API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

| | |
|--------------------------|---|
| **Tables Ingested** | `SentinelOneActivities_CL` |
| | `SentinelOneAgents_CL` |
| | `SentinelOneAlerts_CL` |
| | `SentinelOneGroups_CL` |
| | `SentinelOneThreats_CL` |
| **Connector Definition Files** | [connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Data%20Connectors/SentinelOne_ccp/connectorDefinition.json) |

[→ View full connector details](../connectors/sentineloneccp.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SentinelOneActivities_CL` | [SentinelOne](../connectors/sentineloneccp.md) |
| `SentinelOneAgents_CL` | [SentinelOne](../connectors/sentineloneccp.md) |
| `SentinelOneAlerts_CL` | [SentinelOne](../connectors/sentineloneccp.md) |
| `SentinelOneGroups_CL` | [SentinelOne](../connectors/sentineloneccp.md) |
| `SentinelOneThreats_CL` | [SentinelOne](../connectors/sentineloneccp.md) |
| `SentinelOne_CL` | [SentinelOne](../connectors/sentinelone.md) |

[← Back to Solutions Index](../solutions-index.md)
