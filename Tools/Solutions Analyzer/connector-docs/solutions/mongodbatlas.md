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

This solution provides **1 data connector(s)**:

- [MongoDB Atlas Logs](../connectors/mongodbatlaslogsazurefunctions.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`MDBALogTable_CL`](../tables/mdbalogtable-cl.md) | [MongoDB Atlas Logs](../connectors/mongodbatlaslogsazurefunctions.md) | - |

## Additional Documentation

> 📄 *Source: [MongoDBAtlas/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAtlas/README.md)*

# MongoDB Atlas API Connector for Microsoft Sentinel
Author: Steve Lord. 

Contributor: Lester Szeto

This custom data connector uses a Function App to pull MongoDB Atlas (MDBA) logs from the MongoDB Atlas Administration API and upload them into the selected Log Analytics workspace via the Log Ingestion API. 

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#view/Microsoft_Azure_CreateUIDef/CustomDeploymentBlade/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMongoDBAtlas%2FData%20Connectors%2FMongoDBAtlasLogs%2Fazuredeploy_Connector_MongoDBAtlasLogs_AzureFunction.json/uiFormDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMongoDBAtlas%2FData%20Connectors%2FMongoDBAtlasLogs%2FcreateUiDef.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#view/Microsoft_Azure_CreateUIDef/CustomDeploymentBlade/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMongoDBAtlas%2FData%20Connectors%2FMongoDBAtlasLogs%2Fazuredeploy_Connector_MongoDBAtlasLogs_AzureFunction.json/uiFormDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMongoDBAtlas%2FData%20Connectors%2FMongoDBAtlasLogs%2FcreateUiDef.json)

- [Release Notes](releaseNotes.md)
- [Pre-requisites](#pre-requisites)
- [Deployment Process](#deployment-process)

## **Pre-requisites**
1. An Azure Subscription
2. A Resource Group
2. A Microsoft Sentinel/Log Analytics workspace
3. Roles required to deploy resources:
    - User Access Administrator
    - Contributor
    - Application Administrator
    - Directory Readers
    - Directory Writers
    - Privileged Role Administrator
4. A MongoDB Atlas account:
    - Cluster Id
    - Group Id
    - Client Id
    - Client Secret

## **Deployment Process**
## 1. Deploy Azure Resources
1. Click the **Deploy to Azure** button above.
2. Once in the Azure Portal, select the **Subscription** and **Resource Group** to deploy the resources into.
3. Select a workspace from the list of **Log Analytics Workspaces**.
4. In the MongoDB connection tab, enter fields for the MongoDB Atlas instance from which you are collecting logs
    - Group ID
    - A list of up to 10 Cluster IDs, each on a separate line
    - Client ID
    - Client Secret or a Key Vault name containing the Client Secret. Note the key vault, if used, should be created with a Vault Access Policy
5. Review the MongoDB filters. Select logs from at least one category.
6. Scheduling - this uses the [CRON syntax](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=python-v2%2Cisolated-process%2Cnodejs-v4&pivots=programming-language-csharp#ncrontab-expressions) to specify the rate at which the logs are collected. The MongoDB Atlas Administration API will publish new logs every 5 minutes.
7. Click **Review and Create**.

*[Content truncated...]*

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

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
