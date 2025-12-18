# Dataminr Pulse Alerts Data Connector

| | |
|----------|-------|
| **Connector ID** | `DataminrPulseAlerts` |
| **Publisher** | Dataminr |
| **Tables Ingested** | [`DataminrPulse_Alerts_CL`](../tables-index.md#dataminrpulse_alerts_cl) |
| **Used in Solutions** | [Dataminr Pulse](../solutions/dataminr-pulse.md) |
| **Connector Definition Files** | [DataminrPulseAlerts_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Data%20Connectors/DataminrPulseAlerts/DataminrPulseAlerts_FunctionApp.json) |

Dataminr Pulse Alerts Data Connector brings our AI-powered real-time intelligence into Microsoft Sentinel for faster threat detection and response.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Azure Subscription**: Azure Subscription with owner role is required to register an application in Microsoft Entra ID and assign role of contributor to app in resource group.
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Required Dataminr Credentials/permissions**: 

a. Users must have a valid Dataminr Pulse API **client ID** and **secret** to use this data connector.

 b. One or more Dataminr Pulse Watchlists must be configured in the Dataminr Pulse website.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the DataminrPulse in which logs are pushed via Dataminr RTAP and it will ingest logs into Microsoft Sentinel. Furthermore, the connector will fetch the ingested data from the custom logs table and create Threat Intelligence Indicators into Microsoft Sentinel Threat Intelligence. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1- Credentials for the Dataminr Pulse Client ID and Client Secret**

 * Obtain Dataminr Pulse user ID/password and API client ID/secret from your Dataminr Customer Success Manager (CSM).

**STEP 2- Configure Watchlists in Dataminr Pulse portal.**

 Follow the steps in this section to configure watchlists in portal:

 1. **Login** to the Dataminr Pulse [website](https://app.dataminr.com).

 2. Click on the settings gear icon, and select **Manage Lists**.

 3. Select the type of Watchlist you want to create (Cyber, Topic, Company, etc.) and click the **New List** button.

 4. Provide a **name** for your new Watchlist, and select a highlight color for it, or keep the default color.

 5. When you are done configuring the Watchlist, click **Save** to save it.

**STEP 3 - App Registration steps for the Application in Microsoft Entra ID**

 This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:
 1. Sign in to the [Azure portal](https://portal.azure.com/).
 2. Search for and select **Microsoft Entra ID**.
 3. Under **Manage**, select **App registrations > New registration**.
 4. Enter a display **Name** for your application.
 5. Select **Register** to complete the initial app registration.
 6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the **Application (client) ID** and **Tenant ID**. The client ID and Tenant ID is required as configuration parameters for the execution of DataminrPulse Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)

**STEP 4 - Add a client secret for application in Microsoft Entra ID**

 Sometimes called an application password, a client secret is a string value required for the execution of DataminrPulse Data Connector. Follow the steps in this section to create a new Client Secret:
 1. In the Azure portal, in **App registrations**, select your application.
 2. Select **Certificates & secrets > Client secrets > New client secret**.
 3. Add a description for your client secret.
 4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
 5. Select **Add**. 
 6. *Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page.* The secret value is required as configuration parameter for the execution of DataminrPulse Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret)

**STEP 5 - Assign role of Contributor to application in Microsoft Entra ID**

 Follow the steps in this section to assign the role:
 1. In the Azure portal, Go to **Resource Group** and select your resource group.
 2. Go to **Access control (IAM)** from left panel.
 3. Click on **Add**, and then select **Add role assignment**.
 4. Select **Contributor** as role and click on next.
 5. In **Assign access to**, select `User, group, or service principal`.
 6. Click on **add members** and type **your app name** that you have created and select it.
 7. Now click on **Review + assign** and then again click on **Review + assign**. 

> **Reference link:** [https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal](https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal)

**STEP 6 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Dataminr Pulse Microsoft Sentinel data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following) readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**7. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the DataminrPulse connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-DataminrPulseAlerts-azuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-DataminrPulseAlerts-azuredeploy-gov)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the below information : 

	 a. **Function Name** 

	 b. **Location**: The location in which the data collection rules and data collection endpoints should be deployed. 

	 c. **Workspace**: Enter Workspace ID of log analytics Workspace ID 

	 d. **Workspace Key**: Enter Primary Key of log analytics Workspace 

	 e. **DataminrBaseURL**: Enter Base URL starting with "https://" followed by hostname (Example: https://gateway.dataminr.com/) 

	 f. **ClientId**: Enter your Dataminr account Client ID 

	 g. **ClientSecret**: Enter your Dataminr account Client Secret 

	 h. **AzureEntraObjectID**: Enter Object id of your Microsoft Entra App 

	 i. **AlertsTableName**: Enter name of the table used to store Dataminr Alerts logs. Default is 'DataminrPulse_Alerts' 

	 j. **AzureClientId**: Enter Azure Client ID that you have created during app registration 

	 k. **AzureClientSecret**: Enter Azure Client Secret that you have created during creating the client secret 

	 l. **AzureTenantId**: Enter Azure Tenant ID of your Azure Active Directory 

	 m. **AzureResourceGroupName**: Enter Azure Resource Group Name in which you want deploy the data connector 

	 n. **AzureWorkspaceName**: Enter Microsoft Sentinel Workspace Name of Log Analytics workspace 

	 o. **AzureSubscriptionId**: Enter Azure Subscription Id which is present in the subscription tab in Microsoft Sentinel 

	 p. **LogLevel**: Add log level or log severity value. Default is 'INFO' 

	 q. **Schedule**: Enter a valid Quartz Cron-Expression (Example: 0 0 0 * * *) 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**8. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Dataminr Pulse Microsoft Sentinel data connector manually with Azure Functions (Deployment via Visual Studio Code).

**9. 1) Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-DataminrPulseAlerts-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. DmPulseXXXXX).

	e. **Select a runtime:** Choose Python 3.8 or above.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**10. 2) Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with their respective values (case-sensitive):   

	 a. **Function Name** 

	 b. **Location**: The location in which the data collection rules and data collection endpoints should be deployed. 

	 c. **Workspace**: Enter Workspace ID of log analytics Workspace ID 

	 d. **Workspace Key**: Enter Primary Key of log analytics Workspace 

	 e. **DataminrBaseURL**: Enter Base URL starting with "https://" followed by hostname (Example: https://gateway.dataminr.com/) 

	 f. **ClientId**: Enter your Dataminr account Client ID 

	 g. **ClientSecret**: Enter your Dataminr account Client Secret 

	 h. **AzureEntraObjectID**: Enter Object id of your Microsoft Entra App 

	 i. **AlertsTableName**: Enter name of the table used to store Dataminr Alerts logs. Default is 'DataminrPulse_Alerts' 

	 j. **AzureClientId**: Enter Azure Client ID that you have created during app registration 

	 k. **AzureClientSecret**: Enter Azure Client Secret that you have created during creating the client secret 

	 l. **AzureTenantId**: Enter Azure Tenant ID of your Azure Active Directory 

	 m. **AzureResourceGroupName**: Enter Azure Resource Group Name in which you want deploy the data connector 

	 n. **AzureWorkspaceName**: Enter Microsoft Sentinel Workspace Name of Log Analytics workspace 

	 o. **AzureSubscriptionId**: Enter Azure Subscription Id which is present in the subscription tab in Microsoft Sentinel 

	 p. **LogLevel**: Add log level or log severity value. Default is 'INFO' 

	 q. **Schedule**: Enter a valid Quartz Cron-Expression (Example: 0 0 0 * * *) 

	 r. **logAnalyticsUri** (optional) 
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
4. Once all application settings have been entered, click **Save**.

**STEP 7 - Post Deployment steps**

**12. 1) Get the Function app endpoint**

1. Go to Azure function Overview page and Click on **"Functions"** in the left blade.
2. Click on the function called **"DataminrPulseAlertsHttpStarter"**.
3. Go to **"GetFunctionurl"** and copy the function url.
4. Replace **{functionname}**  with **"DataminrPulseAlertsSentinelOrchestrator"** in copied function url.

**13. 2) To add integration settings in Dataminr RTAP using the function URL**

1. Open any API request tool like Postman.
2. Click on '+' to create a new request.
3. Select HTTP request method as **'POST'**.
4. Enter the url prepapred in **point 1)**, in the request URL part.
5. In Body, select raw JSON and provide request body as below(case-sensitive): 
		{ 
		 "integration-settings": "ADD", 
		 "url": "`(URL part from copied Function-url)`", 
		 "token": "`(value of code parameter from copied Function-url)`" 
		}
6. After providing all required details, click **Send**.
7. You will receive an integration setting ID in the HTTP response with a status code of 200.
8. Save **Integration ID** for future reference.

*Now we are done with the adding integration settings for Dataminr RTAP. Once the Dataminr RTAP send an alert data, Function app is triggered and you should be able to see the Alerts data from the Dataminr Pulse into LogAnalytics workspace table called "DataminrPulse_Alerts_CL".*

[← Back to Connectors Index](../connectors-index.md)
