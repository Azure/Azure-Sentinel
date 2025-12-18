# Cisco Cloud Security

| | |
|----------|-------|
| **Connector ID** | `CiscoUmbrellaDataConnector` |
| **Publisher** | Cisco |
| **Tables Ingested** | [`Cisco_Umbrella_audit_CL`](../tables-index.md#cisco_umbrella_audit_cl), [`Cisco_Umbrella_cloudfirewall_CL`](../tables-index.md#cisco_umbrella_cloudfirewall_cl), [`Cisco_Umbrella_dlp_CL`](../tables-index.md#cisco_umbrella_dlp_cl), [`Cisco_Umbrella_dns_CL`](../tables-index.md#cisco_umbrella_dns_cl), [`Cisco_Umbrella_fileevent_CL`](../tables-index.md#cisco_umbrella_fileevent_cl), [`Cisco_Umbrella_firewall_CL`](../tables-index.md#cisco_umbrella_firewall_cl), [`Cisco_Umbrella_intrusion_CL`](../tables-index.md#cisco_umbrella_intrusion_cl), [`Cisco_Umbrella_ip_CL`](../tables-index.md#cisco_umbrella_ip_cl), [`Cisco_Umbrella_proxy_CL`](../tables-index.md#cisco_umbrella_proxy_cl), [`Cisco_Umbrella_ravpnlogs_CL`](../tables-index.md#cisco_umbrella_ravpnlogs_cl), [`Cisco_Umbrella_ztaflow_CL`](../tables-index.md#cisco_umbrella_ztaflow_cl), [`Cisco_Umbrella_ztna_CL`](../tables-index.md#cisco_umbrella_ztna_cl) |
| **Used in Solutions** | [CiscoUmbrella](../solutions/ciscoumbrella.md) |
| **Connector Definition Files** | [CiscoUmbrella_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Data%20Connectors/CiscoUmbrella_API_FunctionApp.json) |

The Cisco Cloud Security solution for Microsoft Sentinel enables you to ingest [Cisco Secure Access](https://docs.sse.cisco.com/sse-user-guide/docs/welcome-cisco-secure-access) and [Cisco Umbrella](https://docs.umbrella.com/umbrella-user-guide/docs/getting-started) [logs](https://docs.sse.cisco.com/sse-user-guide/docs/manage-your-logs) stored in Amazon S3 into Microsoft Sentinel using the Amazon S3 REST API. Refer to [Cisco Cloud Security log management documentation](https://docs.umbrella.com/deployment-umbrella/docs/log-management) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Amazon S3 REST API Credentials/permissions**: **AWS Access Key Id**, **AWS Secret Access Key**, **AWS S3 Bucket Name** are required for Amazon S3 REST API.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Amazon S3 REST API to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**NOTE:** This connector has been updated to support [Cisco Cloud Security log schema version 14.](https://docs.umbrella.com/deployment-umbrella/docs/log-formats-and-versioning)

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Functions App.

>**NOTE:** This connector uses a parser based on a Kusto Function to normalize fields. [Follow these steps](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Parsers/CiscoUmbrella/Cisco_Umbrella) to create the Kusto function alias **Cisco_Umbrella**.

**STEP 1 - Configuration of the Cisco Cloud Security logs collection**

[See documentation](https://docs.umbrella.com/deployment-umbrella/docs/log-management#section-logging-to-amazon-s-3) and follow the instructions for set up logging and obtain credentials.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Functions**

>**IMPORTANT:** Before deploying the Cisco Cloud Security data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Amazon S3 REST API Authorization credentials, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the Cisco Cloud Security data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinelciscoumbrellaazuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinelciscoumbrellaazuredeploy-gov)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **S3Bucket**, **AWSAccessKeyId**, **AWSSecretAccessKey**
**Note:** For the S3Bucket use the value that Cisco referrs to as the _S3 Bucket Data Path_ and add a / (forward slash) to the end of the value
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**.
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the Cisco Cloud Security data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-python) for Azure Functions development.

1. Download the [Azure Functions App](https://aka.ms/sentinel-CiscoUmbrellaConn-functionapp) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeploymentWithPythonVersion3.9.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		WorkspaceID
		WorkspaceKey
		S3Bucket
		AWSAccessKeyId
		AWSSecretAccessKey
		logAnalyticsUri (optional)
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
3. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
