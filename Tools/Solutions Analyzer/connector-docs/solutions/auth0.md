# Auth0

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-08-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Auth0 Access Management](../connectors/auth0.md)

**Publisher:** Auth0

### [Auth0 Logs](../connectors/auth0connectorccpdefinition.md)

**Publisher:** Microsoft

The [Auth0](https://auth0.com/docs/api/management/v2/logs/get-logs) data connector allows ingesting logs from Auth0 API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses Auth0 API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

| | |
|--------------------------|---|
| **Tables Ingested** | `Auth0Logs_CL` |
| **Connector Definition Files** | [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0/Data%20Connectors/Auth0_CCP/DataConnectorDefinition.json) |

[→ View full connector details](../connectors/auth0connectorccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Auth0AM_CL` | [Auth0 Access Management](../connectors/auth0.md) |
| `Auth0Logs_CL` | [Auth0 Logs](../connectors/auth0connectorccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
