# MongoDBAudit

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAudit) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] MongoDB Audit](../connectors/mongodb.md)

**Publisher:** MongoDB

MongoDB data connector provides the capability to ingest [MongoDBAudit](https://www.mongodb.com/) into Microsoft Sentinel. Refer to [MongoDB documentation](https://www.mongodb.com/docs/manual/tutorial/getting-started/) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `MongoDBAudit_CL` |
| **Connector Definition Files** | [Connector_MongoDBAudit.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAudit/Data%20Connectors/Connector_MongoDBAudit.json) |

[→ View full connector details](../connectors/mongodb.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MongoDBAudit_CL` | [[Deprecated] MongoDB Audit](../connectors/mongodb.md) |

[← Back to Solutions Index](../solutions-index.md)
