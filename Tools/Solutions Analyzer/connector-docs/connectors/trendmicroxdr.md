# Trend Vision One

| | |
|----------|-------|
| **Connector ID** | `TrendMicroXDR` |
| **Publisher** | Trend Micro |
| **Tables Ingested** | [`TrendMicro_XDR_OAT_CL`](../tables-index.md#trendmicro_xdr_oat_cl), [`TrendMicro_XDR_RCA_Result_CL`](../tables-index.md#trendmicro_xdr_rca_result_cl), [`TrendMicro_XDR_RCA_Task_CL`](../tables-index.md#trendmicro_xdr_rca_task_cl), [`TrendMicro_XDR_WORKBENCH_CL`](../tables-index.md#trendmicro_xdr_workbench_cl) |
| **Used in Solutions** | [Trend Micro Vision One](../solutions/trend-micro-vision-one.md) |
| **Connector Definition Files** | [TrendMicroXDR.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Vision%20One/Data%20Connectors/TrendMicroXDR.json) |

The [Trend Vision One](https://www.trendmicro.com/en_us/business/products/detection-response/xdr.html) connector allows you to easily connect your Workbench alert data with Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities. This gives you more insight into your organization's networks/systems and improves your security operation capabilities.



The Trend Vision One connector is supported in Microsoft Sentinel in the following regions: Australia East, Australia Southeast, Brazil South, Canada Central, Canada East, Central India, Central US, East Asia, East US, East US 2, France Central, Japan East, Korea Central, North Central US, North Europe, Norway East, South Africa North, South Central US, Southeast Asia, Sweden Central, Switzerland North, UAE North, UK South, UK West, West Europe, West US, West US 2, West US 3.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Trend Vision One API Token**: A Trend Vision One API Token is required. See the documentation to learn more about the [Trend Vision One API](https://docs.trendmicro.com/documentation/article/trend-vision-one-api-keys-third-party-apps).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Trend Vision One API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Configuration steps for the Trend Vision One API**

 [Follow these instructions](https://docs.trendmicro.com/documentation/article/trend-vision-one-api-keys-third-party-apps) to create an account and an API authentication token.

**STEP 2 - Use the below deployment option to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Trend Vision One connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Trend Vision One API Authorization Token, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Azure Resource Manager (ARM) Template Deployment**

This method provides an automated deployment of the Trend Vision One connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-trendmicroxdr-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter a unique **Function Name**, **Workspace ID**, **Workspace Key**, **API Token** and **Region Code**. 
 - Note: Provide the appropriate region code based on where your Trend Vision One instance is deployed: us, eu, au, in, sg, jp  
 - Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

[← Back to Connectors Index](../connectors-index.md)
