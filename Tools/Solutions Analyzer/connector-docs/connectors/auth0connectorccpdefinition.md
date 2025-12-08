# Auth0 Logs

| | |
|----------|-------|
| **Connector ID** | `Auth0ConnectorCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`Auth0Logs_CL`](../tables-index.md#auth0logs_cl) |
| **Used in Solutions** | [Auth0](../solutions/auth0.md) |
| **Connector Definition Files** | [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0/Data%20Connectors/Auth0_CCP/DataConnectorDefinition.json) |

The [Auth0](https://auth0.com/docs/api/management/v2/logs/get-logs) data connector allows ingesting logs from Auth0 API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses Auth0 API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

[← Back to Connectors Index](../connectors-index.md)
