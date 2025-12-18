# Oracle Cloud Infrastructure

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Oracle Cloud Infrastructure (via Codeless Connector Framework)](../connectors/oci-connector-ccp-definition.md)

**Publisher:** Microsoft

### [[DEPRECATED] Oracle Cloud Infrastructure](../connectors/oraclecloudinfrastructurelogsconnector.md)

**Publisher:** Oracle

The Oracle Cloud Infrastructure (OCI) data connector provides the capability to ingest OCI Logs from [OCI Stream](https://docs.oracle.com/iaas/Content/Streaming/Concepts/streamingoverview.htm) into Microsoft Sentinel using the [OCI Streaming REST API](https://docs.oracle.com/iaas/api/#/streaming/streaming/20180418).



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **OCI API Credentials**:  **API Key Configuration File** and **Private Key** are required for OCI API connection. See the documentation to learn more about [creating keys for API access](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm)

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector can go over the 500 column limit of log Analytics. When this happens some logs will be dropped. For this reason the connector can be unrealiable depending on the logs that are being generated and collected.

>**NOTE:** This connector uses Azure Functions to connect to the Azure Blob Storage API to pull logs into Microsoft Sentinel. This might result in additional costs for data ingestion and for storing data in Azure Blob Storage costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) and [Azure Blob Storage pricing page](https://azure.microsoft.com/pricing/details/storage/blobs/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**OCILogs**](https://aka.ms/sentinel-OracleCloudInfrastructureLogsConnector-parser) which is deployed with the Microsoft Sentinel Solution.

**STEP 1 - Creating Stream**

1. Log in to OCI console and go to *navigation menu* -> *Analytics & AI* -> *Streaming*
2. Click *Create Stream*
3. Select Stream Pool or create a new one
4. Provide the *Stream Name*, *Retention*, *Number of Partitions*, *Total Write Rate*, *Total Read Rate* based on your data amount.
5. Go to *navigation menu* -> *Logging* -> *Service Connectors*
6. Click *Create Service Connector*
6. Provide *Connector Name*, *Description*, *Resource Compartment*
7. Select Source: Logging
8. Select Target: Streaming
9. (Optional) Configure *Log Group*, *Filters* or use custom search query to stream only logs that you need.
10. Configure Target - select the strem created before.
11. Click *Create*

Check the documentation to get more information about [Streaming](https://docs.oracle.com/en-us/iaas/Content/Streaming/home.htm) and [Service Connectors](https://docs.oracle.com/en-us/iaas/Content/service-connector-hub/home.htm).

**STEP 2 - Creating credentials for OCI REST API**

Follow the documentation to [create Private Key and API Key Configuration File.](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm)

>**IMPORTANT:** Save Private Key and API Key Configuration File created during this step as they will be used during deployment step.

**STEP 3 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the OCI data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as OCI API credentials, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the OCI data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-OracleCloudInfrastructureLogsConnector-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Microsoft Sentinel Workspace Id**, **Microsoft Sentinel Shared Key**, **User**, **Key_content**, **Pass_phrase**, **Fingerprint**, **Tenancy**, **Region**, **Message Endpoint**, **Stream Ocid**
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**.
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the OCI data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    1.  Download the [Azure Function App](https://aka.ms/sentinel-OracleCloudInfrastructureLogsConnector-functionapp) file. Extract archive to your local development computer..
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Configuration**.
3. In the **Application settings** tab, select **+ New application setting**.
4. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		AzureSentinelWorkspaceId
		AzureSentinelSharedKey
		user
		key_content
		pass_phrase (Optional)
		fingerprint
		tenancy
		region
		Message Endpoint
		StreamOcid
		logAnalyticsUri (Optional)
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://WORKSPACE_ID.ods.opinsights.azure.us`.
5. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `OCI_Logs_CL` |
| **Connector Definition Files** | [OCI_logs_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Data%20Connectors/OCI_logs_API_FunctionApp.json) |

[→ View full connector details](../connectors/oraclecloudinfrastructurelogsconnector.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OCI_LogsV2_CL` | [Oracle Cloud Infrastructure (via Codeless Connector Framework)](../connectors/oci-connector-ccp-definition.md) |
| `OCI_Logs_CL` | [[DEPRECATED] Oracle Cloud Infrastructure](../connectors/oraclecloudinfrastructurelogsconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
