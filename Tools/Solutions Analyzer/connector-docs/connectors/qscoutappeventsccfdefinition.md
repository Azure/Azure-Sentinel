# QscoutAppEventsConnector

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `QscoutAppEventsCCFDefinition` |
| **Publisher** | Quokka |
| **Used in Solutions** | [Quokka](../solutions/quokka.md) |
| **Collection Method** | CCF |
| **Connector Definition Files** | [QuokkaQscoutAppEventsLogs_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Quokka/Data%20Connectors/QuokkaQscoutAppEventsLogs_ccf/QuokkaQscoutAppEventsLogs_connectorDefinition.json) |

Ingest Qscout application events into Microsoft Sentinel

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`QscoutAppEvents_CL`](../tables/qscoutappevents-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required

**Custom Permissions:**
- **Qscout organization id**: The API requires your organization ID in Qscout.
- **Qscout organization API key**: The API requires your organization API key in Qscout.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Codeless Connector Framework (CCF) to connect to the Qscout app events feed and ingest data into Microsoft Sentinel

Provide the required values below:
- **Qscout Organization ID**: 123456
- **Qscout Organization API Key**: abcdxyz
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
