# 1Password

| | |
|----------|-------|
| **Connector ID** | `1Password` |
| **Publisher** | 1Password |
| **Tables Ingested** | [`OnePasswordEventLogs_CL`](../tables-index.md#onepasswordeventlogs_cl) |
| **Used in Solutions** | [1Password](../solutions/1password.md) |
| **Connector Definition Files** | [1Password_data_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Data%20Connectors/deployment/1Password_data_connector.json) |

The [1Password](https://www.1password.com) solution for Microsoft Sentinel enables you to ingest 1Password logs and events into Microsoft Sentinel. The connector provides visibility into 1Password Events and Alerts in Microsoft Sentinel to improve monitoring and investigation capabilities.



**Underlying Microsoft Technologies used:**



This solution takes a dependency on the following technologies, and some of these dependencies either may be in [Preview](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) state or might result in additional ingestion or operational costs:



-  [Azure Functions](https://azure.microsoft.com/services/functions/#overview)

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **1Password API Token**: A 1Password API Token is required. [See the documentation to learn more about the 1Password API](https://developer.1password.com/docs/events-api/reference). **Note:** A 1Password account is required

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to 1Password to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Configuration steps for the 1Password API**

 [Follow these instructions](https://support.1password.com/events-reporting/#appendix-issue-or-revoke-bearer-tokens) provided by 1Password to obtain an API Token. **Note:** A 1Password account is required

**STEP 2 - Deploy the functionApp using DeployToAzure button to create the table, dcr and the associated Azure Function**

>**IMPORTANT:** Before deploying the 1Password connector, a custom table needs to be created.

**3. Option 1 - Azure Resource Manager (ARM) Template**

This method provides an automated deployment of the 1Password connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-OnePassword-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace Name**, **Workspace Name**, **API Key**, and **URI**.
 - The default **Time Interval** is set to pull the last five (5) minutes of data. If the time interval needs to be modified, it is recommended to change the Function App Timer Trigger accordingly (in the function.json file, post deployment) to prevent overlapping data ingestion.
 - Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

[← Back to Connectors Index](../connectors-index.md)
