# SentinelOne

| | |
|----------|-------|
| **Connector ID** | `SentinelOneCCP` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SentinelOneActivities_CL`](../tables-index.md#sentineloneactivities_cl), [`SentinelOneAgents_CL`](../tables-index.md#sentineloneagents_cl), [`SentinelOneAlerts_CL`](../tables-index.md#sentinelonealerts_cl), [`SentinelOneGroups_CL`](../tables-index.md#sentinelonegroups_cl), [`SentinelOneThreats_CL`](../tables-index.md#sentinelonethreats_cl) |
| **Used in Solutions** | [SentinelOne](../solutions/sentinelone.md) |
| **Connector Definition Files** | [connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Data%20Connectors/SentinelOne_ccp/connectorDefinition.json) |

The [SentinelOne](https://usea1-nessat.sentinelone.net/api-doc/overview) data connector allows ingesting logs from the SentinelOne API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the SentinelOne API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### Configuration steps for the SentinelOne API 
 Follow the instructions to obtain the credentials. You can also follow the [guide](https://usea1-nessat.sentinelone.net/docs/en/how-to-automate-api-token-generation.html#how-to-automate-api-token-generation) to generate API key.
#### 1. Retrieve SentinelOne Management URL
   1.1. Log in to the SentinelOne [**Management Console**] with Admin user credentials
   1.2. In the [**Management Console**] copy the URL link above without the URL path.
#### 2. Retrieve API Token
   2.1. Log in to the SentinelOne [**Management Console**] with Admin user credentials
 2.2. In the [**Management Console**], click [**Settings**]
  2.3. In [**Settings**] view click on [**USERS**].
   2.4. In the [**USERS**] Page click on [**Service Users**] -> [**Actions**] -> [**Create new service user**].
   2.5. Choose [**Expiration date**] and [**scope**] (by site) and click on [**Create User**].
   2.6. Once the [**Service User**] is created copy the [**API Token**] from page and press [**Save**]
- **SentinelOne Management URL**: https://example.sentinelone.net/
- **API Token**: API Token
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
