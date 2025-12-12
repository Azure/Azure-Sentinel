# Rapid7InsightVM

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Rapid7InsightVM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Rapid7InsightVM) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Rapid7 Insight Platform Vulnerability Management Reports](../connectors/insightvmcloudapi.md)

**Publisher:** Rapid7

The [Rapid7 Insight VM](https://www.rapid7.com/products/insightvm/) Report data connector provides the capability to ingest Scan reports and vulnerability data into Microsoft Sentinel through the REST API from the  Rapid7 Insight platform (Managed in the cloud). Refer to [API documentation](https://docs.rapid7.com/insight/api-overview/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials**: **InsightVMAPIKey** is required for REST API. [See the documentation to learn more about API](https://docs.rapid7.com/insight/api-overview/). Check all [requirements and follow  the instructions](https://docs.rapid7.com/insight/managing-platform-api-keys/) for obtaining credentials

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Insight VM API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a parsers based on a Kusto Function to work as expected [**InsightVMAssets**](https://aka.ms/sentinel-InsightVMAssets-parser) and [**InsightVMVulnerabilities**](https://aka.ms/sentinel-InsightVMVulnerabilities-parser) which is deployed with the Microsoft Sentinel Solution.

**STEP 1 - Configuration steps for the Insight VM Cloud**

 [Follow the instructions](https://docs.rapid7.com/insight/managing-platform-api-keys/) to obtain the credentials.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Workspace data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the Rapid7 Insight Vulnerability Management Report data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-InsightVMCloudAPI-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
> **NOTE:** Within the same resource group, you can't mix Windows and Linux apps in the same region. Select existing resource group without Windows apps in it or create new resource group.
3. Enter the **InsightVMAPIKey**, choose **InsightVMCloudRegion** and deploy. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the Rapid7 Insight Vulnerability Management Report data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    1. Download the [Azure Function App](https://github.com/averbn/azure_sentinel_data_connectors/raw/main/insight-vm-cloud-azure-sentinel-data-connector/InsightVMCloudAPISentinelConn.zip) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive):  
		InsightVMAPIKey
		InsightVMCloudRegion
		WorkspaceID
		WorkspaceKey
		logAnalyticsUri (optional)
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
3. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `NexposeInsightVMCloud_assets_CL` |
| | `NexposeInsightVMCloud_vulnerabilities_CL` |
| **Connector Definition Files** | [InsightVMCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Rapid7InsightVM/Data%20Connectors/InsightVMCloud_API_FunctionApp.json) |

[→ View full connector details](../connectors/insightvmcloudapi.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `NexposeInsightVMCloud_assets_CL` | [Rapid7 Insight Platform Vulnerability Management Reports](../connectors/insightvmcloudapi.md) |
| `NexposeInsightVMCloud_vulnerabilities_CL` | [Rapid7 Insight Platform Vulnerability Management Reports](../connectors/insightvmcloudapi.md) |

[← Back to Solutions Index](../solutions-index.md)
