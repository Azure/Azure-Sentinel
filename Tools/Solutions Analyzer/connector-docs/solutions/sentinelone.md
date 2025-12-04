# SentinelOne

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-11-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### SentinelOne

**Publisher:** SentinelOne

The [SentinelOne](https://www.sentinelone.com/) data connector provides the capability to ingest common SentinelOne server objects such as Threats, Agents, Applications, Activities, Policies, Groups, and more events into Microsoft Sentinel through the REST API. Refer to API documentation: `https://<SOneInstanceDomain>.sentinelone.net/api-doc/overview` for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

**Tables Ingested:**

- `SentinelOne_CL`

**Connector Definition Files:**

- [SentinelOne_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Data%20Connectors/SentinelOne_API_FunctionApp.json)

### SentinelOne

**Publisher:** Microsoft

The [SentinelOne](https://usea1-nessat.sentinelone.net/api-doc/overview) data connector allows ingesting logs from the SentinelOne API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the SentinelOne API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

**Tables Ingested:**

- `SentinelOneActivities_CL`
- `SentinelOneAgents_CL`
- `SentinelOneAlerts_CL`
- `SentinelOneGroups_CL`
- `SentinelOneThreats_CL`

**Connector Definition Files:**

- [connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Data%20Connectors/SentinelOne_ccp/connectorDefinition.json)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SentinelOneActivities_CL` | SentinelOne |
| `SentinelOneAgents_CL` | SentinelOne |
| `SentinelOneAlerts_CL` | SentinelOne |
| `SentinelOneGroups_CL` | SentinelOne |
| `SentinelOneThreats_CL` | SentinelOne |
| `SentinelOne_CL` | SentinelOne |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n