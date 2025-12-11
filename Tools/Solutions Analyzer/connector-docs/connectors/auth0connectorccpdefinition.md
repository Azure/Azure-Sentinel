# Auth0 Logs

| | |
|----------|-------|
| **Connector ID** | `Auth0ConnectorCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`Auth0Logs_CL`](../tables-index.md#auth0logs_cl) |
| **Used in Solutions** | [Auth0](../solutions/auth0.md) |
| **Connector Definition Files** | [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0/Data%20Connectors/Auth0_CCP/DataConnectorDefinition.json) |

The [Auth0](https://auth0.com/docs/api/management/v2/logs/get-logs) data connector allows ingesting logs from Auth0 API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses Auth0 API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### STEP 1 - Configuration steps for the Auth0 Management API
Follow the instructions to obtain the credentials. 
 1. In Auth0 Dashboard, go to [**Applications > Applications**]
 2. Select your Application. This should be a [**Machine-to-Machine**] Application configured with at least [**read:logs**] and [**read:logs_users**] permissions. 
 3. Copy [**Domain, ClientID, Client Secret**]
- **Base API URL**: https://example.auth0.com
- **Client ID**: Client ID
- **Client Secret**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
