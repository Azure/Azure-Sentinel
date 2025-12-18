# AbnormalSecurity 

| | |
|----------|-------|
| **Connector ID** | `AbnormalSecurity` |
| **Publisher** | AbnormalSecurity |
| **Tables Ingested** | [`ABNORMAL_CASES_CL`](../tables-index.md#abnormal_cases_cl), [`ABNORMAL_THREAT_MESSAGES_CL`](../tables-index.md#abnormal_threat_messages_cl) |
| **Used in Solutions** | [AbnormalSecurity](../solutions/abnormalsecurity.md) |
| **Connector Definition Files** | [AbnormalSecurity_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbnormalSecurity/Data%20Connectors/AbnormalSecurity_API_FunctionApp.json) |

The Abnormal Security data connector provides the capability to ingest threat and case logs into Microsoft Sentinel using the [Abnormal Security Rest API.](https://app.swaggerhub.com/apis/abnormal-security/abx/)

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Abnormal Security API Token**: An Abnormal Security API Token is required. [See the documentation to learn more about Abnormal Security API](https://app.swaggerhub.com/apis/abnormal-security/abx/). **Note:** An Abnormal Security account is required

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to Abnormal Security's REST API to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

**STEP 1 - Configuration steps for the Abnormal Security API**

 [Follow these instructions](https://app.swaggerhub.com/apis/abnormal-security/abx) provided by Abnormal Security to configure the REST API integration. **Note:** An Abnormal Security account is required

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Abnormal Security data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Abnormal Security API Authorization Token, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Azure Resource Manager (ARM) Template**

This method provides an automated deployment of the Abnormal Security connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-abnormalsecurity-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Microsoft Sentinel Workspace ID**, **Microsoft Sentinel Shared Key** and **Abnormal Security REST API Key**.
 - The default **Time Interval** is set to pull the last five (5) minutes of data. If the time interval needs to be modified, it is recommended to change the Function App Timer Trigger accordingly (in the function.json file, post deployment) to prevent overlapping data ingestion.
 4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Abnormal Security data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-python) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-abnormalsecurity-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. AbnormalSecurityXX).

	e. **Select a runtime:** Choose Python 3.11.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		SENTINEL_WORKSPACE_ID
		SENTINEL_SHARED_KEY
		ABNORMAL_SECURITY_REST_API_TOKEN
		logAnalyticsUri (optional)
(add any other settings required by the Function App)
Set the `uri` value to: `<add uri value>` 
>Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Azure Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details.
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us.` 
4. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
