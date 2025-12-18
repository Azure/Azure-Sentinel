# Cisco Cloud Security (using elastic premium plan)

| | |
|----------|-------|
| **Connector ID** | `CiscoUmbrellaDataConnectorelasticpremium` |
| **Publisher** | Cisco |
| **Tables Ingested** | [`Cisco_Umbrella_audit_CL`](../tables-index.md#cisco_umbrella_audit_cl), [`Cisco_Umbrella_cloudfirewall_CL`](../tables-index.md#cisco_umbrella_cloudfirewall_cl), [`Cisco_Umbrella_dlp_CL`](../tables-index.md#cisco_umbrella_dlp_cl), [`Cisco_Umbrella_dns_CL`](../tables-index.md#cisco_umbrella_dns_cl), [`Cisco_Umbrella_fileevent_CL`](../tables-index.md#cisco_umbrella_fileevent_cl), [`Cisco_Umbrella_firewall_CL`](../tables-index.md#cisco_umbrella_firewall_cl), [`Cisco_Umbrella_intrusion_CL`](../tables-index.md#cisco_umbrella_intrusion_cl), [`Cisco_Umbrella_ip_CL`](../tables-index.md#cisco_umbrella_ip_cl), [`Cisco_Umbrella_proxy_CL`](../tables-index.md#cisco_umbrella_proxy_cl), [`Cisco_Umbrella_ravpnlogs_CL`](../tables-index.md#cisco_umbrella_ravpnlogs_cl), [`Cisco_Umbrella_ztaflow_CL`](../tables-index.md#cisco_umbrella_ztaflow_cl), [`Cisco_Umbrella_ztna_CL`](../tables-index.md#cisco_umbrella_ztna_cl) |
| **Used in Solutions** | [CiscoUmbrella](../solutions/ciscoumbrella.md) |
| **Connector Definition Files** | [CiscoUmbrella_API_FunctionApp_elasticpremium.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Data%20Connectors/CiscoUmbrella_API_FunctionApp_elasticpremium.json) |

The Cisco Umbrella data connector provides the capability to ingest [Cisco Umbrella](https://docs.umbrella.com/) events stored in Amazon S3 into Microsoft Sentinel using the Amazon S3 REST API. Refer to [Cisco Umbrella log management documentation](https://docs.umbrella.com/deployment-umbrella/docs/log-management) for more information.



**NOTE:** This data connector uses the [Azure Functions Premium Plan](https://learn.microsoft.com/azure/azure-functions/functions-premium-plan?tabs=portal) to enable secure ingestion capabilities and will incur additional costs. More pricing details are [here](https://azure.microsoft.com/pricing/details/functions/?msockid=2f4366822d836a7c2ac673462cfc6ba8#pricing).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Amazon S3 REST API Credentials/permissions**: **AWS Access Key Id**, **AWS Secret Access Key**, **AWS S3 Bucket Name** are required for Amazon S3 REST API.
- **Virtual Network permissions (for private access)**: For private storage account access, **Network Contributor** permissions are required on the Virtual Network and subnet. The subnet must be delegated to **Microsoft.Web/serverFarms** for Function App VNet integration.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Amazon S3 REST API to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**NOTE:** This connector has been updated to support [cisco umbrella log schema version 14.](https://docs.umbrella.com/deployment-umbrella/docs/log-formats-and-versioning)

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Functions App.

>**NOTE:** This connector uses a parser based on a Kusto Function to normalize fields. [Follow these steps](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Parsers/CiscoUmbrella/Cisco_Umbrella) to create the Kusto function alias **Cisco_Umbrella**.

**STEP 1 - Network Prerequisites for Private Access**

>**IMPORTANT:** When deploying with private storage account access, ensure the following network prerequisites are met:
> - **Virtual Network**: An existing Virtual Network (VNet) must be available
> - **Subnet**: A dedicated subnet within the VNet must be delegated to **Microsoft.Web/serverFarms** for Function App VNet integration
> - **Subnet Delegation**: Configure the subnet delegation using Azure Portal, ARM template, or Azure CLI:
>   - Azure Portal: Go to Virtual networks → Select your VNet → Subnets → Select subnet → Delegate subnet to service → Choose **Microsoft.Web/serverFarms**
>   - Azure CLI: `az network vnet subnet update --resource-group <rg-name> --vnet-name <vnet-name> --name <subnet-name> --delegations Microsoft.Web/serverFarms`
> - **Private Endpoints**: The deployment will create private endpoints for storage account services (blob, file, queue, table) within the same subnet

**STEP 2 - Configuration of the Cisco Umbrella logs collection**

[See documentation](https://docs.umbrella.com/deployment-umbrella/docs/log-management#section-logging-to-amazon-s-3) and follow the instructions for set up logging and obtain credentials.

**STEP 3 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Functions**

>**IMPORTANT:** Before deploying the Cisco Umbrella data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Amazon S3 REST API Authorization credentials, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the Cisco Umbrella data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinelciscoumbrellaelasticpremiumazuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinelciscoumbrellaelasticpremiumazuredeploy-gov)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **S3Bucket**, **AWSAccessKeyId**, **AWSSecretAccessKey**
4. **For Private Access Deployment**: Also enter **existingVnetName**, **existingVnetResourceGroupName**, and **existingSubnetName** (ensure subnet is delegated to Microsoft.Web/serverFarms)
**Note:** For the S3Bucket use the value that Cisco referrs to as the _S3 Bucket Data Path_ and add a / (forward slash) to the end of the value
5. Mark the checkbox labeled **I agree to the terms and conditions stated above**.
6. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the Cisco Umbrella data connector manually with Azure Functions (Deployment via Visual Studio Code).
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
