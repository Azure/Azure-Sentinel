# ImpervaCloudWAF

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-09-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Imperva Cloud WAF](../connectors/impervacloudwaflogsccfdefinition.md)

**Publisher:** Microsoft

### [Imperva Cloud WAF](../connectors/impervawafcloudapi.md)

**Publisher:** Imperva

The [Imperva Cloud WAF](https://www.imperva.com/resources/resource-library/datasheets/imperva-cloud-waf/) data connector provides the capability to integrate and ingest Web Application Firewall events into Microsoft Sentinel through the REST API. Refer to Log integration [documentation](https://docs.imperva.com/bundle/cloud-application-security/page/settings/log-integration.htm#Download) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **ImpervaAPIID**, **ImpervaAPIKey**, **ImpervaLogServerURI** are required for the API. [See the documentation to learn more about Setup Log Integration process](https://docs.imperva.com/bundle/cloud-application-security/page/settings/log-integration.htm#Setuplogintegration). Check all [requirements and follow  the instructions](https://docs.imperva.com/bundle/cloud-application-security/page/settings/log-integration.htm#Setuplogintegration) for obtaining credentials. Please note that this connector uses CEF log event format. [More information](https://docs.imperva.com/bundle/cloud-application-security/page/more/log-file-structure.htm#Logfilestructure) about log format.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Imperva Cloud API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Functions App.

>**NOTE:**This data connector depends on a parser based on a Kusto Function to work as expected [**ImpervaWAFCloud**](https://aka.ms/sentinel-impervawafcloud-parser) which is deployed with the Microsoft Sentinel Solution.

**STEP 1 - Configuration steps for the Log Integration**

 [Follow the instructions](https://docs.imperva.com/bundle/cloud-application-security/page/settings/log-integration.htm#Setuplogintegration) to obtain the credentials.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Functions**

>**IMPORTANT:** Before deploying the Workspace data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Imperva Cloud WAF data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-impervawafcloud-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
> **NOTE:** Within the same resource group, you can't mix Windows and Linux apps in the same region. Select existing resource group without Windows apps in it or create new resource group.
3. Enter the **ImpervaAPIID**, **ImpervaAPIKey**, **ImpervaLogServerURI** and deploy. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Imperva Cloud WAF data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure functions development.

1. Download the [Azure Functions App](https://aka.ms/sentinel-impervawafcloud-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. ImpervaCloudXXXXX).

	e. **Select a runtime:** Choose Python 3.11.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select ** New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		ImpervaAPIID
		ImpervaAPIKey
		ImpervaLogServerURI
		WorkspaceID
		WorkspaceKey
		logAnalyticsUri (optional)
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
3. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `ImpervaWAFCloud_CL` |
| **Connector Definition Files** | [ImpervaWAFCloud_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Data%20Connectors/ImpervaWAFCloud_FunctionApp.json) |

[→ View full connector details](../connectors/impervawafcloudapi.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ImpervaWAFCloudV2_CL` | [Imperva Cloud WAF](../connectors/impervacloudwaflogsccfdefinition.md) |
| `ImpervaWAFCloud_CL` | [Imperva Cloud WAF](../connectors/impervawafcloudapi.md) |

[← Back to Solutions Index](../solutions-index.md)
