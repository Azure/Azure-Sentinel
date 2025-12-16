# [DEPRECATED] Cloudflare

| | |
|----------|-------|
| **Connector ID** | `CloudflareDataConnector` |
| **Publisher** | Cloudflare |
| **Tables Ingested** | [`Cloudflare_CL`](../tables-index.md#cloudflare_cl) |
| **Used in Solutions** | [Cloudflare](../solutions/cloudflare.md) |
| **Connector Definition Files** | [Cloudflare_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Data%20Connectors/Cloudflare_API_FunctionApp.json) |

The Cloudflare data connector provides the capability to ingest [Cloudflare logs](https://developers.cloudflare.com/logs/) into Microsoft Sentinel using the Cloudflare Logpush and Azure Blob Storage. Refer to [Cloudflare  documentation](https://developers.cloudflare.com/logs/logpush) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Azure Blob Storage connection string and container name**: Azure Blob Storage connection string and container name where the logs are pushed to by Cloudflare Logpush. [See the documentation to learn more about creating Azure Blob Storage container.](https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-portal)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Azure Blob Storage API to pull logs into Microsoft Sentinel. This might result in additional costs for data ingestion and for storing data in Azure Blob Storage costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) and [Azure Blob Storage pricing page](https://azure.microsoft.com/pricing/details/storage/blobs/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**Cloudflare**](https://aka.ms/sentinel-CloudflareDataConnector-parser) which is deployed with the Microsoft Sentinel Solution.

**STEP 1 - Configuration of the Cloudflare Logpush**

See documentation to [setup Cloudflare Logpush to Microsoft Azure](https://developers.cloudflare.com/logs/logpush/logpush-dashboard)

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Cloudflare data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as Azure Blob Storage connection string and container name, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Cloudflare data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-CloudflareDataConnector-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Azure Blob Storage Container Name**, **Azure Blob Storage Connection String**, **Microsoft Sentinel Workspace Id**, **Microsoft Sentinel Shared Key**
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**.
5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Cloudflare data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-python) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-CloudflareDataConnector-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. CloudflareXX).

	e. **Select a runtime:** Choose Python 3.11.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		CONTAINER_NAME
		AZURE_STORAGE_CONNECTION_STRING
		WORKSPACE_ID
		SHARED_KEY
		logAnalyticsUri (Optional)
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://WORKSPACE_ID.ods.opinsights.azure.us`. 
4. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
