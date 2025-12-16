# HolmSecurity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Holm Security |
| **Support Tier** | Partner |
| **Support Link** | [https://support.holmsecurity.com/](https://support.holmsecurity.com/) |
| **Categories** | domains |
| **First Published** | 2022-07-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HolmSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HolmSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Holm Security Asset Data](../connectors/holmsecurityassets.md)

**Publisher:** Holm Security

The connector provides the capability to poll data from Holm Security Center into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Holm Security API Token**: Holm Security API Token is required. [Holm Security API Token](https://support.holmsecurity.com/)

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to a Holm Security Assets to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Configuration steps for the Holm Security API**

 [Follow these instructions](https://support.holmsecurity.com/knowledge/how-do-i-set-up-an-api-token) to create an API authentication token.

**STEP 2 - Use the below deployment option to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Holm Security connector, have the Workspace ID  and Workspace Primary Key (can be copied from the following), as well as the Holm Security API authorization Token, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Azure Resource Manager (ARM) Template Deployment**

**Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Holm Security connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-holmsecurityassets-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **API Username**, **API Password**, 'and/or Other required fields'. 
>Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

| | |
|--------------------------|---|
| **Tables Ingested** | `net_assets_CL` |
| | `web_assets_CL` |
| **Connector Definition Files** | [HolmSecurityAssets_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HolmSecurity/Data%20Connectors/HolmSecurityAssets_API_FunctionApp.json) |

[→ View full connector details](../connectors/holmsecurityassets.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `net_assets_CL` | [Holm Security Asset Data](../connectors/holmsecurityassets.md) |
| `web_assets_CL` | [Holm Security Asset Data](../connectors/holmsecurityassets.md) |

[← Back to Solutions Index](../solutions-index.md)
