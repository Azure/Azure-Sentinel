# MongoDBAtlas

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `MDBALogTable_CL` |
| **Connector Definition Files** | [MongoDBAtlasLogs_AzureFunction.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAtlas/Data%20Connectors/MongoDBAtlasLogs/MongoDBAtlasLogs_AzureFunction.json) |

[→ View full connector details](../connectors/mongodbatlaslogsazurefunctions.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MDBALogTable_CL` | [MongoDB Atlas Logs](../connectors/mongodbatlaslogsazurefunctions.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                                 |
|-------------|--------------------------------|----------------------------------------------------------------------------------------------------|
| 3.0.8       | 05-11-2025                     | Fix slow UI for MongoDB Cluster ID validation.                                                     |
| 3.0.7       | 29-10-2025                     | Update extension bundle version, minor instructions update, publisherId update.                    |
| 3.0.6       | 17-10-2025                     | Add ability to pass MongoDB Client Secret via a key vault. Improve concurrency model used to ingest logs.|
| 3.0.5       | 08-10-2025                     | Removal of workspace creation. Add ability to pull logs from multiple MongoDB clusters.            |
| 3.0.4       | 01-10-2025                     | Deployment UI updates. Fix Deploy to Azure button.                                                 |
| 3.0.3       | 29-09-2025                     | Fixed a bug in log filtering. Some improvements to UI text.                                        |
| 3.0.2       | 25-09-2025                     | Fixed bad link to logo in Solution json. Fixed Deploy to Azure links.                              |
| 3.0.1       | 18-09-2025                     | Improved filtering by log ID. Performance improvement to upload via Log Ingestion API in parallel. |
| 3.0.0       | 17-09-2025                     | Initial Solution Release                                                                           |

[← Back to Solutions Index](../solutions-index.md)
