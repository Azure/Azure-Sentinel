# GitHub

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview)](../connectors/githubauditdefinitionv2.md)

**Publisher:** Microsoft

### [[Deprecated] GitHub Enterprise Audit Log](../connectors/githubecauditlogpolling.md)

**Publisher:** GitHub

### [GitHub (using Webhooks)](../connectors/githubwebhook.md)

**Publisher:** Microsoft

The [GitHub](https://www.github.com) webhook data connector provides the capability to ingest GitHub subscribed events into Microsoft Sentinel using [GitHub webhook events](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads). The connector provides ability to get events into Microsoft Sentinel which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more. 



 **Note:** If you are intended to ingest Github Audit logs, Please refer to GitHub Enterprise Audit Log Connector from "**Data Connectors**" gallery.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector has been built on http trigger based Azure Function. And it provides an endpoint to which github will be connected through it's webhook capability and posts the subscribed events into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Github Webhook connector, have the Workspace ID  and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the GitHub data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-GitHubwebhookAPI-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
> **NOTE:** Within the same resource group, you can't mix Windows and Linux apps in the same region and deploy. 
3. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the GitHub webhook data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    1. Download the [Azure Function App](https://aka.ms/sentinel-GitHubWebhookAPI-functionapp) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration. 
2. In the Function App, select the Function App Name and select **Configuration**.
3. In the **Application settings** tab, select ** New application setting**.
4. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		WorkspaceID
		WorkspaceKey
		logAnalyticsUri (optional) - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
4. Once all application settings have been entered, click **Save**.

**Post Deployment steps**

**STEP 1 - To get the Azure Function url**

  1. Go to Azure function Overview page and Click on "Functions" in the left blade.
 2. Click on the function called "GithubwebhookConnector".
 3. Go to "GetFunctionurl" and copy the function url.

  **STEP 2 - Configure Webhook to Github Organization**

  1. Go to [GitHub](https://www.github.com) and open your account and click on "Your Organizations."
 2. Click on Settings.
 3. Click on "Webhooks" and enter the function app url which was copied from above STEP 1 under payload URL textbox. 
 4. Choose content type as "application/json". 
 5. Subscribe for events and Click on "Add Webhook"

*Now we are done with the github Webhook configuration. Once the github events triggered and after the delay of 20 to 30 mins (As there will be a dealy for LogAnalytics to spin up the resources for the first time), you should be able to see all the transactional events from the Github into LogAnalytics workspace table called "githubscanaudit_CL".*

 For more details, Click [here](https://aka.ms/sentinel-gitHubwebhooksteps)

| | |
|--------------------------|---|
| **Tables Ingested** | `githubscanaudit_CL` |
| **Connector Definition Files** | [GithubWebhook_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Data%20Connectors/GithubWebhook/GithubWebhook_API_FunctionApp.json) |

[→ View full connector details](../connectors/githubwebhook.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GitHubAuditLogPolling_CL` | [[Deprecated] GitHub Enterprise Audit Log](../connectors/githubecauditlogpolling.md) |
| `GitHubAuditLogsV2_CL` | [GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview)](../connectors/githubauditdefinitionv2.md) |
| `githubscanaudit_CL` | [GitHub (using Webhooks)](../connectors/githubwebhook.md) |

[← Back to Solutions Index](../solutions-index.md)
