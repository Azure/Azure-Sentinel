# BigID DSPM connector

| | |
|----------|-------|
| **Connector ID** | `BigIDDSPMLogsConnectorDefinition` |
| **Publisher** | BigID |
| **Tables Ingested** | [`BigIDDSPMCatalog_CL`](../tables-index.md#bigiddspmcatalog_cl) |
| **Used in Solutions** | [BigID](../solutions/bigid.md) |
| **Connector Definition Files** | [BigIDDSPMLogs_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BigID/Data%20Connectors/BigIDDSPMLogs_ccp/BigIDDSPMLogs_connectorDefinition.json) |

The [BigID DSPM](https://bigid.com/data-security-posture-management/) data connector provides the capability to ingest BigID DSPM cases with affected objects and datasource information into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **BigID DSPM API access**: Access to the BigID DSPM API through a BigID Token is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to BigID DSPM API to start collecting BigID DSPM cases and affected Objects in Microsoft Sentinel**

Provide your BigID domain name like 'customer.bigid.cloud' and your BigID token. Generate a token in the BigID console via Settings -> Access Management -> Users -> Select User and generate a token.
- **BigID FQDN**: BigID FQDN
- **BigID Token**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
