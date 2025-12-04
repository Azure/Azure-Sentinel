# Auth0

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-08-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### Auth0 Access Management

**Publisher:** Auth0

The [Auth0 Access Management](https://auth0.com/access-management) data connector provides the capability to ingest [Auth0 log events](https://auth0.com/docs/api/management/v2/#!/Logs/get_logs) into Microsoft Sentinel

**Tables Ingested:**

- `Auth0AM_CL`

**Connector Definition Files:**

- [Auth0_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0/Data%20Connectors/Auth0_FunctionApp.json)

### Auth0 Logs

**Publisher:** Microsoft

The [Auth0](https://auth0.com/docs/api/management/v2/logs/get-logs) data connector allows ingesting logs from Auth0 API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses Auth0 API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

**Tables Ingested:**

- `Auth0Logs_CL`

**Connector Definition Files:**

- [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0/Data%20Connectors/Auth0_CCP/DataConnectorDefinition.json)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Auth0AM_CL` | Auth0 Access Management |
| `Auth0Logs_CL` | Auth0 Logs |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n