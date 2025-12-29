# Check Point Cyberint IOC Connector

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `CheckPointCyberintIOC` |
| **Publisher** | Checkpoint Cyberint |
| **Used in Solutions** | [Check Point Cyberint IOC](../solutions/check-point-cyberint-ioc.md) |
| **Collection Method** | CCF |
| **Connector Definition Files** | [CyberintArgosIOCLogs_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20Cyberint%20IOC/Data%20Connectors/CyberintArgosIOCLogs_ccp/CyberintArgosIOCLogs_connectorDefinition.json) |

This is data connector for Check Point Cyberint IOC.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`iocsent_CL`](../tables/iocsent-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Check Point Cyberint API Key and Argos URL**: The connector API key and Argos URL are required

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Checkpoint Cyberint Alerts to Microsoft Sentinel**

To enable the connector provide the required information below and click on Connect.
>
- **Argos URL**: Argos URL
- **API key**: API key
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
