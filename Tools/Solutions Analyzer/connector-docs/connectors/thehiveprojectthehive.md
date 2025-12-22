# TheHive Project - TheHive

| | |
|----------|-------|
| **Connector ID** | `TheHiveProjectTheHive` |
| **Publisher** | TheHive Project |
| **Tables Ingested** | [`TheHive_CL`](../tables-index.md#thehive_cl) |
| **Used in Solutions** | [TheHive](../solutions/thehive.md) |
| **Connector Definition Files** | [TheHive_Webhooks_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive/Data%20Connectors/TheHive_Webhooks_FunctionApp.json) |

The [TheHive](http://thehive-project.org/) data connector provides the capability to ingest common TheHive events into Microsoft Sentinel through Webhooks. TheHive can notify external system of modification events (case creation, alert update, task assignment) in real time. When a change occurs in the TheHive, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://docs.thehive-project.org/thehive/legacy/thehive3/admin/webhooks/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Webhooks Credentials/permissions**: **TheHiveBearerToken**, **Callback URL** are required for working Webhooks. See the documentation to learn more about [configuring Webhooks](https://docs.thehive-project.org/thehive/installation-and-configuration/configuration/webhooks/).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector uses Azure Functions based on HTTP Trigger for waiting POST requests with logs to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**TheHive**](https://aka.ms/sentinel-TheHive-parser) which is deployed with the Microsoft Sentinel Solution.

**STEP 1 - Configuration steps for the TheHive**

 Follow the [instructions](https://docs.thehive-project.org/thehive/installation-and-configuration/configuration/webhooks/) to configure Webhooks.

1. Authentication method is *Beared Auth*.
2. Generate the **TheHiveBearerToken** according to your password policy.
3. Setup Webhook notifications in the *application.conf* file including **TheHiveBearerToken** parameter.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the TheHive data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the TheHive data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-TheHive-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
> **NOTE:** Within the same resource group, you can't mix Windows and Linux apps in the same region. Select existing resource group without Windows apps in it or create new resource group.
3. Enter the **TheHiveBearerToken** and deploy. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.
6. After deploying open Function App page, select your app, go to the **Functions** and click **Get Function Url** copy it and follow p.7 from STEP 1.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the TheHive data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-TheHive-functionapp) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select ** New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		TheHiveBearerToken
		WorkspaceID
		WorkspaceKey
		logAnalyticsUri (optional)
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
4. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
