# [DEPRECATED] Slack Audit

| | |
|----------|-------|
| **Connector ID** | `SlackAuditAPI` |
| **Publisher** | Slack |
| **Tables Ingested** | [`SlackAudit_CL`](../tables-index.md#slackaudit_cl) |
| **Used in Solutions** | [SlackAudit](../solutions/slackaudit.md) |
| **Connector Definition Files** | [SlackAudit_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Data%20Connectors/SlackAudit_API_FunctionApp.json) |

The [Slack](https://slack.com) Audit data connector provides the capability to ingest [Slack Audit Records](https://api.slack.com/admins/audit-logs) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs#the_audit_event) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **SlackAPIBearerToken** is required for REST API. [See the documentation to learn more about API](https://api.slack.com/web#authentication). Check all [requirements and follow  the instructions](https://api.slack.com/web#authentication) for obtaining credentials.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Slack REST API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected. [Follow these steps](https://aka.ms/sentinel-SlackAuditAPI-parser) to create the Kusto functions alias, **SlackAudit**

**STEP 1 - Configuration steps for the Slack API**

 [Follow the instructions](https://api.slack.com/web#authentication) to obtain the credentials.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Slack Audit data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the Slack Audit data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-SlackAuditAPI-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
> **NOTE:** Within the same resource group, you can't mix Windows and Linux apps in the same region. Select existing resource group without Windows apps in it or create new resource group.
3. Enter the **SlackAPIBearerToken** and deploy. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the Slack Audit data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    1. Download the [Azure Function App](https://aka.ms/sentinel-SlackAuditAPI-functionapp) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Configuration**.
3. In the **Application settings** tab, select ** New application setting**.
4. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		SlackAPIBearerToken
		WorkspaceID
		WorkspaceKey
		logAnalyticsUri (optional)
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
3. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
