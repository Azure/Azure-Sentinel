# Tenable.io Vulnerability Management

| | |
|----------|-------|
| **Connector ID** | `TenableIOAPI` |
| **Publisher** | Tenable |
| **Tables Ingested** | [`Tenable_IO_Assets_CL`](../tables-index.md#tenable_io_assets_cl), [`Tenable_IO_Vuln_CL`](../tables-index.md#tenable_io_vuln_cl) |
| **Used in Solutions** | [TenableIO](../solutions/tenableio.md) |
| **Connector Definition Files** | [TenableIO.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO/Data%20Connectors/TenableIO.json) |

The [Tenable.io](https://www.tenable.com/products/tenable-io) data connector provides the capability to ingest Asset and Vulnerability data into Microsoft Sentinel through the REST API from the Tenable.io platform (Managed in the cloud). Refer to [API documentation](https://developer.tenable.com/reference) for more information. The connector provides the ability to get data which helps to examine potential security risks, get insight into your computing assets, diagnose configuration problems and more

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: Both a **TenableAccessKey** and a **TenableSecretKey** is required to access the Tenable REST API. [See the documentation to learn more about API](https://developer.tenable.com/reference#vulnerability-management). Check all [requirements and follow  the instructions](https://docs.tenable.com/tenableio/vulnerabilitymanagement/Content/Settings/GenerateAPIKey.htm) for obtaining credentials.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Durable Functions to connect to the Tenable.io API to pull [assets](https://developer.tenable.com/reference#exports-assets-download-chunk) and [vulnerabilities](https://developer.tenable.com/reference#exports-vulns-request-export) at a regular interval into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a [**Tenable.io parser for vulnerabilities**](https://aka.ms/sentinel-TenableIO-TenableIOVulnerabilities-parser) and a [**Tenable.io parser for assets**](https://aka.ms/sentinel-TenableIO-TenableIOAssets-parser) based on a Kusto Function to work as expected which is deployed with the Microsoft Sentinel Solution.

**STEP 1 - Configuration steps for Tenable.io**

 [Follow the instructions](https://docs.tenable.com/tenableio/vulnerabilitymanagement/Content/Settings/GenerateAPIKey.htm) to obtain the required API credentials.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function App**

>**IMPORTANT:** Before deploying the Workspace data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Tenable.io Vulnerability Management Report data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-TenableIO-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **TenableAccessKey** and **TenableSecretKey** and deploy. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Tenable.io Vulnerability Management Report data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-TenableIO-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. TenableIOXXXXX).

	e. **Select a runtime:** Choose Python 3.8.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		TenableAccessKey
		TenableSecretKey
		WorkspaceID
		WorkspaceKey
		logAnalyticsUri (optional)
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<WorkspaceID>.ods.opinsights.azure.us`.
3. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
