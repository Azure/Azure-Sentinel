# Box

| | |
|----------|-------|
| **Connector ID** | `BoxDataConnector` |
| **Publisher** | Box |
| **Tables Ingested** | [`BoxEvents_CL`](../tables-index.md#boxevents_cl) |
| **Used in Solutions** | [Box](../solutions/box.md) |
| **Connector Definition Files** | [Box_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Data%20Connectors/Box_API_FunctionApp.json) |

The Box data connector provides the capability to ingest [Box enterprise's events](https://developer.box.com/guides/events/#admin-events) into Microsoft Sentinel using the Box REST API. Refer to [Box  documentation](https://developer.box.com/guides/events/enterprise-events/for-enterprise/) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Box API Credentials**: Box config JSON file is required for Box REST API JWT authentication. [See the documentation to learn more about JWT authentication](https://developer.box.com/guides/authentication/jwt/).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Box REST API to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This connector depends on a parser based on Kusto Function to work as expected [**BoxEvents**](https://aka.ms/sentinel-BoxDataConnector-parser) which is deployed with the Microsoft Sentinel Solution.

**STEP 1 - Configuration of the Box events collection**

See documentation to [setup JWT authentication](https://developer.box.com/guides/authentication/jwt/jwt-setup/) and [obtain JSON file with credentials](https://developer.box.com/guides/authentication/jwt/with-sdk/#prerequisites).

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Box data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Box JSON configuration file, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the Box data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-BoxDataConnector-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **AzureSentinelWorkspaceId**, **AzureSentinelSharedKey**, **BoxConfigJSON**
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**.
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the Box data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    1. Download the [Azure Function App](https://aka.ms/sentinel-BoxDataConnector-functionapp) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Configuration**.
3. In the **Application settings** tab, select **+ New application setting**.
4. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		AzureSentinelWorkspaceId
		AzureSentinelSharedKey
		BOX_CONFIG_JSON
		logAnalyticsUri (optional)
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
5. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
