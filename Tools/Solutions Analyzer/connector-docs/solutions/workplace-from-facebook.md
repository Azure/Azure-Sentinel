# Workplace from Facebook

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Workplace from Facebook](../connectors/workplacefacebook.md)

**Publisher:** Facebook

The [Workplace](https://www.workplace.com/) data connector provides the capability to ingest common Workplace events into Microsoft Sentinel through Webhooks. Webhooks enable custom integration apps to subscribe to events in Workplace and receive updates in real time. When a change occurs in Workplace, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://developers.facebook.com/docs/workplace/reference/webhooks) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Webhooks Credentials/permissions**: WorkplaceAppSecret, WorkplaceVerifyToken, Callback URL are required for working Webhooks. See the documentation to learn more about [configuring Webhooks](https://developers.facebook.com/docs/workplace/reference/webhooks), [configuring permissions](https://developers.facebook.com/docs/workplace/reference/permissions).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector uses Azure Functions based on HTTP Trigger for waiting POST requests with logs to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Functions App.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias WorkplaceFacebook and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook/Parsers/Workplace_Facebook.txt) on the second line of the query, enter the hostname(s) of your Workplace Facebook device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

**STEP 1 - Configuration steps for the Workplace**

 Follow the instructions to configure Webhooks.

1. Log in to the Workplace with Admin user credentials.
2. In the Admin panel, click **Integrations**.
3. In the **All integrations** view, click **Create custom integration**
4. Enter the name and description and click **Create**.
5. In the **Integration details** panel show **App secret** and copy.
6. In the **Integration permissions** pannel set all read permissions. Refer to [permission page](https://developers.facebook.com/docs/workplace/reference/permissions) for details.
7. Now proceed to STEP 2 to follow the steps (listed in Option 1 or 2) to Deploy the Azure Function.
8. Enter the requested parameters and also enter a Token of choice. Copy this Token / Note it for the upcoming step.
9. After the deployment of Azure Functions completes successfully, open Function App page, select your app, go to **Functions**, click **Get Function URL** and copy this / Note it for the upcoming step.
10. Go back to Workplace from Facebook. In the **Configure webhooks** panel on each Tab set **Callback URL** as the same value that you copied in point 9 above and Verify token as the same
 value you copied in point 8 above which was obtained during STEP 2 of Azure Functions deployment.
11. Click Save.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Functions**

>**IMPORTANT:** Before deploying the Workplace data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the Workplace data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-WorkplaceFacebook-azuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-WorkplaceFacebook-azuredeploy-gov)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
> **NOTE:** Within the same resource group, you can't mix Windows and Linux apps in the same region. Select existing resource group without Windows apps in it or create new resource group.
3. Enter the **WorkplaceVerifyToken** (can be any expression, copy and save it for STEP 1), **WorkplaceAppSecret** and deploy. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.
6. After deploying open Function App page, select your app, go to the **Functions** and click **Get Function Url** copy it and follow p.7 from STEP 1.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the Sophos Endpoint Protection data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-WorkplaceFacebook-functionapp) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select ** New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		WorkplaceAppSecret
		WorkplaceVerifyToken
		WorkspaceID
		WorkspaceKey
		logAnalyticsUri (optional)
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
4. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `Workplace_Facebook_CL` |
| **Connector Definition Files** | [WorkplaceFacebook_Webhooks_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook/Data%20Connectors/WorkplaceFacebook/WorkplaceFacebook_Webhooks_FunctionApp.json) |

[→ View full connector details](../connectors/workplacefacebook.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Workplace_Facebook_CL` | [Workplace from Facebook](../connectors/workplacefacebook.md) |

[← Back to Solutions Index](../solutions-index.md)
