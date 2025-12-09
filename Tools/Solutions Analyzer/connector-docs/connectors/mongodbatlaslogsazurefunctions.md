# MongoDB Atlas Logs

| | |
|----------|-------|
| **Connector ID** | `MongoDBAtlasLogsAzureFunctions` |
| **Publisher** | MongoDB |
| **Tables Ingested** | [`MDBALogTable_CL`](../tables-index.md#mdbalogtable_cl) |
| **Used in Solutions** | [MongoDBAtlas](../solutions/mongodbatlas.md) |
| **Connector Definition Files** | [MongoDBAtlasLogs_AzureFunction.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAtlas/Data%20Connectors/MongoDBAtlasLogs/MongoDBAtlasLogs_AzureFunction.json) |

The [MongoDBAtlas](https://www.mongodb.com/products/platform/atlas-database) Logs connector gives the capability to upload MongoDB Atlas database logs into Microsoft Sentinel through the MongoDB Atlas Administration API. Refer to the [API documentation](https://www.mongodb.com/docs/api/doc/atlas-admin-api-v2/) for more information. The connector provides the ability to get a range of database log messages for the specified hosts and specified project.

[← Back to Connectors Index](../connectors-index.md)
