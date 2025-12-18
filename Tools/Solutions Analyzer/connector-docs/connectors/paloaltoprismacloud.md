# [DEPRECATED] Palo Alto Prisma Cloud CSPM

| | |
|----------|-------|
| **Connector ID** | `PaloAltoPrismaCloud` |
| **Publisher** | Palo Alto |
| **Tables Ingested** | [`PaloAltoPrismaCloudAlert_CL`](../tables-index.md#paloaltoprismacloudalert_cl), [`PaloAltoPrismaCloudAudit_CL`](../tables-index.md#paloaltoprismacloudaudit_cl) |
| **Used in Solutions** | [PaloAltoPrismaCloud](../solutions/paloaltoprismacloud.md) |
| **Connector Definition Files** | [PrismaCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Data%20Connectors/PrismaCloud_API_FunctionApp.json) |

The Palo Alto Prisma Cloud CSPM data connector provides the capability to ingest [Prisma Cloud CSPM alerts](https://prisma.pan.dev/api/cloud/cspm/alerts#operation/get-alerts) and [audit logs](https://prisma.pan.dev/api/cloud/cspm/audit-logs#operation/rl-audit-logs) into Microsoft sentinel using the Prisma Cloud CSPM API. Refer to [Prisma Cloud CSPM API documentation](https://prisma.pan.dev/api/cloud/cspm) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Palo Alto Prisma Cloud API Credentials**: **Prisma Cloud API Url**, **Prisma Cloud Access Key ID**, **Prisma Cloud Secret Key** are required for Prisma Cloud API connection. See the documentation to learn more about [creating Prisma Cloud Access Key](https://docs.paloaltonetworks.com/prisma/prisma-cloud/prisma-cloud-admin/manage-prisma-cloud-administrators/create-access-keys.html) and about [obtaining Prisma Cloud API Url](https://prisma.pan.dev/api/cloud/api-urls)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Palo Alto Prisma Cloud REST API to pull logs into Microsoft sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**PaloAltoPrismaCloud**](https://aka.ms/sentinel-PaloAltoPrismaCloud-parser) which is deployed with the Microsoft sentinel Solution.

**STEP 1 - Configuration of the Prisma Cloud**

Follow the documentation to [create Prisma Cloud Access Key](https://docs.paloaltonetworks.com/prisma/prisma-cloud/prisma-cloud-admin/manage-prisma-cloud-administrators/create-access-keys.html) and [obtain Prisma Cloud API Url](https://api.docs.prismacloud.io/reference)

 NOTE: Please use SYSTEM ADMIN role for giving access to Prisma Cloud API because only SYSTEM ADMIN role is allowed to View Prisma Cloud Audit Logs. Refer to [Prisma Cloud Administrator Permissions (paloaltonetworks.com)](https://docs.paloaltonetworks.com/prisma/prisma-cloud/prisma-cloud-admin/manage-prisma-cloud-administrators/prisma-cloud-admin-permissions) for more details of administrator permissions.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Prisma Cloud data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as Prisma Cloud API credentials, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the Prisma Cloud data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-PaloAltoPrismaCloud-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Prisma Cloud API Url**, **Prisma Cloud Access Key ID**, **Prisma Cloud Secret Key**, **Microsoft sentinel Workspace Id**, **Microsoft sentinel Shared Key**
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**.
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the Prisma Cloud data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-python) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-PaloAltoPrismaCloud-functionapp) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Configuration**.
3. In the **Application settings** tab, select **+ New application setting**.
4. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		PrismaCloudAPIUrl
		PrismaCloudAccessKeyID
		PrismaCloudSecretKey
		AzureSentinelWorkspaceId
		AzureSentinelSharedKey
		logAnalyticsUri (Optional)
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://WORKSPACE_ID.ods.opinsights.azure.us`. 
5. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
