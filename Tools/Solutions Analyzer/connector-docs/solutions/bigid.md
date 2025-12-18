# BigID

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | BigID |
| **Support Tier** | Partner |
| **Support Link** | [https://www.bigid.com/support](https://www.bigid.com/support) |
| **Categories** | domains |
| **First Published** | 2025-10-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BigID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BigID) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [BigID DSPM connector](../connectors/bigiddspmlogsconnectordefinition.md)

**Publisher:** BigID

The [BigID DSPM](https://bigid.com/data-security-posture-management/) data connector provides the capability to ingest BigID DSPM cases with affected objects and datasource information into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **BigID DSPM API access**: Access to the BigID DSPM API through a BigID Token is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to BigID DSPM API to start collecting BigID DSPM cases and affected Objects in Microsoft Sentinel**

Provide your BigID domain name like 'customer.bigid.cloud' and your BigID token. Generate a token in the BigID console via Settings -> Access Management -> Users -> Select User and generate a token.
- **BigID FQDN**: BigID FQDN
- **BigID Token**: (password field)
- Click 'Connect' to establish connection

| | |
|--------------------------|---|
| **Tables Ingested** | `BigIDDSPMCatalog_CL` |
| **Connector Definition Files** | [BigIDDSPMLogs_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BigID/Data%20Connectors/BigIDDSPMLogs_ccp/BigIDDSPMLogs_connectorDefinition.json) |

[→ View full connector details](../connectors/bigiddspmlogsconnectordefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BigIDDSPMCatalog_CL` | [BigID DSPM connector](../connectors/bigiddspmlogsconnectordefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
