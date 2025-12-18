# [DEPRECATED] Snowflake

| | |
|----------|-------|
| **Connector ID** | `SnowflakeDataConnector` |
| **Publisher** | Snowflake |
| **Tables Ingested** | [`Snowflake_CL`](../tables-index.md#snowflake_cl) |
| **Used in Solutions** | [Snowflake](../solutions/snowflake.md) |
| **Connector Definition Files** | [Snowflake_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake/Data%20Connectors/Snowflake_API_FunctionApp.json) |

The Snowflake data connector provides the capability to ingest Snowflake [login logs](https://docs.snowflake.com/en/sql-reference/account-usage/login_history.html) and [query logs](https://docs.snowflake.com/en/sql-reference/account-usage/query_history.html) into Microsoft Sentinel using the Snowflake Python Connector. Refer to [Snowflake  documentation](https://docs.snowflake.com/en/user-guide/python-connector.html) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Snowflake Credentials**: **Snowflake Account Identifier**, **Snowflake User** and **Snowflake Password** are required for connection. See the documentation to learn more about [Snowflake Account Identifier](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html#). Instructions on how to create user for this connector you can find below.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Azure Blob Storage API to pull logs into Microsoft Sentinel. This might result in additional costs for data ingestion and for storing data in Azure Blob Storage costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) and [Azure Blob Storage pricing page](https://azure.microsoft.com/pricing/details/storage/blobs/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**Snowflake**](https://aka.ms/sentinel-SnowflakeDataConnector-parser) which is deployed with the Microsoft Sentinel Solution.

**STEP 1 - Creating user in Snowflake**

To query data from Snowflake you need a user that is assigned to a role with sufficient privileges and a virtual warehouse cluster. The initial size of this cluster will be set to small but if it is insufficient, the cluster size can be increased as necessary.

1. Enter the Snowflake console.
2. Switch role to SECURITYADMIN and [create a new role](https://docs.snowflake.com/en/sql-reference/sql/create-role.html):
```
USE ROLE SECURITYADMIN;
CREATE OR REPLACE ROLE EXAMPLE_ROLE_NAME;```
3. Switch role to SYSADMIN and [create warehouse](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse.html) and [grand access](https://docs.snowflake.com/en/sql-reference/sql/grant-privilege.html) to it:
```
USE ROLE SYSADMIN;
CREATE OR REPLACE WAREHOUSE EXAMPLE_WAREHOUSE_NAME
  WAREHOUSE_SIZE = 'SMALL' 
  AUTO_SUSPEND = 5
  AUTO_RESUME = true
  INITIALLY_SUSPENDED = true;
GRANT USAGE, OPERATE ON WAREHOUSE EXAMPLE_WAREHOUSE_NAME TO ROLE EXAMPLE_ROLE_NAME;```
4. Switch role to SECURITYADMIN and [create a new user](https://docs.snowflake.com/en/sql-reference/sql/create-user.html):
```
USE ROLE SECURITYADMIN;
CREATE OR REPLACE USER EXAMPLE_USER_NAME
   PASSWORD = 'example_password'
   DEFAULT_ROLE = EXAMPLE_ROLE_NAME
   DEFAULT_WAREHOUSE = EXAMPLE_WAREHOUSE_NAME
;```
5. Switch role to ACCOUNTADMIN and [grant access to snowflake database](https://docs.snowflake.com/en/sql-reference/account-usage.html#enabling-account-usage-for-other-roles) for role.
```
USE ROLE ACCOUNTADMIN;
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE EXAMPLE_ROLE_NAME;```
6. Switch role to SECURITYADMIN and [assign role](https://docs.snowflake.com/en/sql-reference/sql/grant-role.html) to user:
```
USE ROLE SECURITYADMIN;
GRANT ROLE EXAMPLE_ROLE_NAME TO USER EXAMPLE_USER_NAME;```

>**IMPORTANT:** Save user and API password created during this step as they will be used during deployment step.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as Snowflake credentials, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-SnowflakeDataConnector-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Snowflake Account Identifier**, **Snowflake User**, **Snowflake Password**, **Microsoft Sentinel Workspace Id**, **Microsoft Sentinel Shared Key**
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**.
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    1. Download the [Azure Function App](https://aka.ms/sentinel-SnowflakeDataConnector-functionapp) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration. 
2. In the Function App, select the Function App Name and select **Configuration**.
3. In the **Application settings** tab, select **+ New application setting**.
4. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		SNOWFLAKE_ACCOUNT
		SNOWFLAKE_USER
		SNOWFLAKE_PASSWORD
		WORKSPACE_ID
		SHARED_KEY
		logAnalyticsUri (optional)
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://WORKSPACE_ID.ods.opinsights.azure.us`. 
4. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
