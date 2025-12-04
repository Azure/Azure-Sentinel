# MongoDBAtlas

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | MongoDB |
| **Support Tier** | Partner |
| **Support Link** | [https://www.mongodb.com/company/contact](https://www.mongodb.com/company/contact) |
| **Categories** | domains |
| **First Published** | 2025-08-22 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAtlas](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAtlas) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [MongoDB Atlas Logs](../connectors/mongodbatlaslogsazurefunctions.md)

**Publisher:** MongoDB

The [MongoDBAtlas](https://www.mongodb.com/products/platform/atlas-database) Logs connector gives the capability to upload MongoDB Atlas database logs into Microsoft Sentinel through the MongoDB Atlas Administration API. Refer to the [API documentation](https://www.mongodb.com/docs/api/doc/atlas-admin-api-v2/) for more information. The connector provides the ability to get a range of database log messages for the specified hosts and specified project.

| | |
|--------------------------|---|
| **Tables Ingested** | `MDBALogTable_CL` |
| **Connector Definition Files** | [MongoDBAtlasLogs_AzureFunction.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAtlas/Data%20Connectors/MongoDBAtlasLogs/MongoDBAtlasLogs_AzureFunction.json) |

[→ View full connector details](../connectors/mongodbatlaslogsazurefunctions.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MDBALogTable_CL` | [MongoDB Atlas Logs](../connectors/mongodbatlaslogsazurefunctions.md) |

[← Back to Solutions Index](../solutions-index.md)
