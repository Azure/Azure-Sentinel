# Auth0

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

The [Auth0 Access Management](https://auth0.com/access-management) data connector provides the capability to ingest [Auth0 log events](https://auth0.com/docs/api/management/v2/#!/Logs/get_logs) into Microsoft Sentinel

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Auth0AM_CL` |
| **Connector Definition Files** | [Auth0_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0/Data%20Connectors/Auth0_FunctionApp.json) |

[→ View full connector details](../connectors/auth0.md)

### [Auth0 Logs](../connectors/auth0connectorccpdefinition.md)

**Publisher:** Microsoft

The [Auth0](https://auth0.com/docs/api/management/v2/logs/get-logs) data connector allows ingesting logs from Auth0 API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses Auth0 API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Auth0Logs_CL` |
| **Connector Definition Files** | [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Auth0/Data%20Connectors/Auth0_CCP/DataConnectorDefinition.json) |

[→ View full connector details](../connectors/auth0connectorccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Auth0AM_CL` | [Auth0 Access Management](../connectors/auth0.md) |
| `Auth0Logs_CL` | [Auth0 Logs](../connectors/auth0connectorccpdefinition.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                     |
|-------------|--------------------------------|--------------------------------------------------------|
| 3.1.2       | 10-02-2025                     | Advancing CCP **Data Connector** from Public preview to Global Availability.           |
| 3.1.1       | 22-01-2025                     | Added Preview tag to CCP **Data Connector**                                            |
| 3.1.0       | 13-12-2024                     | Added new CCP **Data Connector** to the Solution                                       |
| 3.0.0       | 24-08-2024                     | Updated the **Data Connector** Function app python runtime version to 3.11             |
|             | 11-12-2023                     | Added new **Parser** (Auth0AM)                                                         |

[← Back to Solutions Index](../solutions-index.md)
