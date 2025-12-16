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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: MongoDB Atlas service account **Client ID** and **Client Secret** are required.  [See the documentation to learn more about creating a service account](https://www.mongodb.com/docs/atlas/configure-api-access/#grant-programmatic-access-to-an-organization)

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to 'MongoDB Atlas' to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>Ensure the workspace is added to Microsoft Sentinel before deploying the connector.

**1. STEP 1 - Configuration steps for the 'MongoDB Atlas Administration API'**

1. [Follow these instructions](https://www.mongodb.com/docs/atlas/configure-api-access/#grant-programmatic-access-to-an-organization) to create a MongoDB Atlas service account.
2. Copy the **Client ID** and **Client Secret** you created, also the **Group ID** (Project) and each **Cluster ID** (Hostname) required for later steps.
3. Refer [MongoDB Atlas API documentation](https://www.mongodb.com/docs/api/doc/atlas-admin-api-v2/operation/operation-downloadgroupclusterlog) for more details.
4. The client secret can be passed into the connector via an Azure key vault or directly into the connector.
5. If you want to use the key vault option create a key vault, using a Vault Access Policy, with a secret named **mongodb-client-secret** and your client secret saved as the secret value.

**2. STEP 2 - Deploy the 'MongoDB Atlas Logs' connector and the associated Azure Function**

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#view/Microsoft_Azure_CreateUIDef/CustomDeploymentBlade/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMongoDBAtlas%2FData%20Connectors%2FMongoDBAtlasLogs%2Fazuredeploy_Connector_MongoDBAtlasLogs_AzureFunction.json/uiFormDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMongoDBAtlas%2FData%20Connectors%2FMongoDBAtlasLogs%2FcreateUiDef.json)

**3. STEP 3 - Set the connector parameters**

1. Select the preferred **Subscription** and an existing **Resource Group**.
2. Enter an existing **Log Analytics Workspace Resource ID** belonging to the resource group.
3. Click **Next**
4. Enter the **MongoDB Group ID**, a list of up to 10 **MongoDB Cluster IDs**, each on a separate line, and **MongoDB Client ID**.
5. Choose for **Authentication Method** either **Client Secret** and copy in your client secret value or **Key Vault** and copy in the name of your key vault. 
Click **Next** 
6. Review the MongoDB filters. Select logs from at least one category. Click **Next** 
7. Review the schedule. Click **Next** 
8. Review the settings then click **Create**.

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
