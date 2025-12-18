# [DEPRECATED] Salesforce Service Cloud

| | |
|----------|-------|
| **Connector ID** | `SalesforceServiceCloud` |
| **Publisher** | Salesforce |
| **Tables Ingested** | [`SalesforceServiceCloudV2_CL`](../tables-index.md#salesforceservicecloudv2_cl), [`SalesforceServiceCloud_CL`](../tables-index.md#salesforceservicecloud_cl) |
| **Used in Solutions** | [Salesforce Service Cloud](../solutions/salesforce-service-cloud.md) |
| **Connector Definition Files** | [SalesforceServiceCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud/Data%20Connectors/SalesforceServiceCloud_API_FunctionApp.json) |

The Salesforce Service Cloud data connector provides the capability to ingest information about your Salesforce operational events into Microsoft Sentinel through the REST API. The connector provides ability to review events in your org on an accelerated basis, get [event log files](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/event_log_file_hourly_overview.htm) in hourly increments for recent activity.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **Salesforce API Username**, **Salesforce API Password**, **Salesforce Security Token**, **Salesforce Consumer Key**, **Salesforce Consumer Secret** is required for REST API. [See the documentation to learn more about API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/quickstart.htm).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Salesforce Lightning Platform REST API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias SalesforceServiceCloud and load the function code or click [here](https://aka.ms/sentinel-SalesforceServiceCloud-parser). The function usually takes 10-15 minutes to activate after solution installation/update.

**STEP 1 - Configuration steps for the Salesforce Lightning Platform REST API**

1. See the [link](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/quickstart.htm) and follow the instructions for obtaining Salesforce API Authorization credentials. 
2. On the **Set Up Authorization** step choose **Session ID Authorization** method.
3. You must provide your client id, client secret, username, and password with user security token.

>**NOTE:** Ingesting data from on an hourly interval may require additional licensing based on the edition of the Salesforce Service Cloud being used. Please refer to [Salesforce documentation](https://www.salesforce.com/editions-pricing/service-cloud/) and/or support for more details.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Salesforce Service Cloud data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Salesforce API Authorization credentials, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the Salesforce Service Cloud data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-SalesforceServiceCloud-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **Salesforce API Username**, **Salesforce API Password**, **Salesforce Security Token**, **Salesforce Consumer Key**, **Salesforce Consumer Secret** and deploy. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the Salesforce Service Cloud data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-SalesforceServiceCloud-functionapp) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Configuration**.
3. In the **Application settings** tab, select **+ New application setting**.
4. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		SalesforceUser
		SalesforcePass
		SalesforceSecurityToken
		SalesforceConsumerKey
		SalesforceConsumerSecret
		WorkspaceID
		WorkspaceKey
		logAnalyticsUri (optional)
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`
5. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
