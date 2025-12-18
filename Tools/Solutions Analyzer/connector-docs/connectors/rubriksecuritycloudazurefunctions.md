# Rubrik Security Cloud data connector

| | |
|----------|-------|
| **Connector ID** | `RubrikSecurityCloudAzureFunctions` |
| **Publisher** | Rubrik, Inc |
| **Tables Ingested** | [`Rubrik_Anomaly_Data_CL`](../tables-index.md#rubrik_anomaly_data_cl), [`Rubrik_Events_Data_CL`](../tables-index.md#rubrik_events_data_cl), [`Rubrik_Ransomware_Data_CL`](../tables-index.md#rubrik_ransomware_data_cl), [`Rubrik_ThreatHunt_Data_CL`](../tables-index.md#rubrik_threathunt_data_cl) |
| **Used in Solutions** | [RubrikSecurityCloud](../solutions/rubriksecuritycloud.md) |
| **Connector Definition Files** | [RubrikWebhookEvents_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Data%20Connectors/RubrikWebhookEvents/RubrikWebhookEvents_FunctionApp.json) |

The Rubrik Security Cloud data connector enables security operations teams to integrate insights from Rubrik's Data Observability services into Microsoft Sentinel. The insights include identification of anomalous filesystem behavior associated with ransomware and mass deletion, assess the blast radius of a ransomware attack, and sensitive data operators to prioritize and more rapidly investigate potential incidents.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Rubrik webhook which push its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Rubrik Microsoft Sentinel data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following) readily available..
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**2. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Rubrik connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-RubrikWebhookEvents-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the below information : 
		Function Name 
		Workspace ID 
		Workspace Key 
		AnomaliesTableName 
		RansomwareAnalysisTableName 
		ThreatHuntsTableName 
		EventsTableName 
		LogLevel 
 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**3. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Rubrik Microsoft Sentinel data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-RubrikWebhookEvents-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. RubrikXXXXX).

	e. **Select a runtime:** Choose Python 3.8 or above.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with their respective values (case-sensitive): 
		WorkspaceID
		WorkspaceKey
		AnomaliesTableName
		RansomwareAnalysisTableName
		ThreatHuntsTableName
		EventsTableName
		LogLevel
		logAnalyticsUri (optional)
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: https://<CustomerId>.ods.opinsights.azure.us. 
4. Once all application settings have been entered, click **Save**.

**Post Deployment steps**

**7. 1) Get the Function app endpoint**

1. Go to Azure function Overview page and Click on **"Functions"** tab.
2. Click on the function called **"RubrikHttpStarter"**.
3. Go to **"GetFunctionurl"** and copy the function url.

**8. 2) Add a webhook in RubrikSecurityCloud to send data to Microsoft Sentinel.**

Follow the Rubrik User Guide instructions to [Add a Webhook](https://docs.rubrik.com/en-us/saas/saas/common/adding_webhook.html) to begin receiving event information  
 1. Select the Microsoft Sentinel as the webhook Provider 
 2. Enter the desired Webhook name 
 3. Enter the URL part from copied Function-url as the webhook URL endpoint and replace **{functionname}**  with **"RubrikAnomalyOrchestrator"**, for the Rubrik Microsoft Sentinel Solution 
 4. Select the EventType as Anomaly 
 5. Select the following severity levels: Critical, Warning, Informational 
 6. Choose multiple log types, if desired, when running **"RubrikEventsOrchestrator"** 
 7. Repeat the same steps to add webhooks for Anomaly Detection Analysis, Threat Hunt and Other Events.
   

 NOTE: while adding webhooks for Anomaly Detection Analysis, Threat Hunt and Other Events, replace **{functionname}**  with **"RubrikRansomwareOrchestrator"**, **"RubrikThreatHuntOrchestrator"** and **"RubrikEventsOrchestrator"** respectively in copied function-url.

*Now we are done with the rubrik Webhook configuration. Once the webhook events triggered , you should be able to see the Anomaly, Anomaly Detection Analysis, Threat Hunt events and Other Events from the Rubrik into respective LogAnalytics workspace table called "Rubrik_Anomaly_Data_CL", "Rubrik_Ransomware_Data_CL", "Rubrik_ThreatHunt_Data_CL", and "Rubrik_Events_Data_CL".*

[← Back to Connectors Index](../connectors-index.md)
