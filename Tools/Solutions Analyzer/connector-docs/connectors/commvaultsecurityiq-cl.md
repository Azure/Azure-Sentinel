# CommvaultSecurityIQ

| | |
|----------|-------|
| **Connector ID** | `CommvaultSecurityIQ_CL` |
| **Publisher** | Commvault |
| **Tables Ingested** | [`CommvaultSecurityIQ_CL`](../tables-index.md#commvaultsecurityiq_cl) |
| **Used in Solutions** | [Commvault Security IQ](../solutions/commvault-security-iq.md) |
| **Connector Definition Files** | [CommvaultSecurityIQ_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Data%20Connectors/CommvaultSecurityIQ_API_AzureFunctionApp.json) |

This Azure Function enables Commvault users to ingest alerts/events into their Microsoft Sentinel instance. With Analytic Rules,Microsoft Sentinel can automatically create Microsoft Sentinel incidents from incoming events and logs.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Commvault Environment Endpoint URL**: Make sure to follow the documentation and set the secret value in KeyVault
- **Commvault QSDK Token**: Make sure to follow the documentation and set the secret value in KeyVault

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to a Commvault Instance to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Configuration steps for the Commvalut QSDK Token**

[Follow these instructions](https://documentation.commvault.com/2024e/essential/creating_access_token.html) to create an API Token.

**STEP 2 - Deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the CommvaultSecurityIQ data connector, have the Workspace ID  and Workspace Primary Key (can be copied from the following), as well as the Commvault Endpoint URL and QSDK Token, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Commvault Security IQ data connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-CommvaultSecurityIQ-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Region**. 
3. Enter the **Workspace ID**, **Workspace Key** 'and/or Other required fields' and click Next. 
4. Click **Create** to deploy.

[← Back to Connectors Index](../connectors-index.md)
