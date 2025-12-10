# Cohesity

| | |
|----------|-------|
| **Connector ID** | `CohesityDataConnector` |
| **Publisher** | Cohesity |
| **Tables Ingested** | [`Cohesity_CL`](../tables-index.md#cohesity_cl) |
| **Used in Solutions** | [CohesitySecurity](../solutions/cohesitysecurity.md) |
| **Connector Definition Files** | [Cohesity_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/Cohesity_API_FunctionApp.json) |

The Cohesity function apps provide the ability to ingest Cohesity Datahawk ransomware alerts into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Azure Blob Storage connection string and container name**: Azure Blob Storage connection string and container name

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions that connect to the Azure Blob Storage and KeyVault. This might result in additional costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/), [Azure Blob Storage pricing page](https://azure.microsoft.com/pricing/details/storage/blobs/) and [Azure KeyVault pricing page](https://azure.microsoft.com/pricing/details/key-vault/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Get a Cohesity DataHawk API key (see troubleshooting [instruction 1](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentProducer))**

**STEP 2 - Register Azure app ([link](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps)) and save Application (client) ID, Directory (tenant) ID, and Secret Value ([instructions](https://learn.microsoft.com/en-us/azure/healthcare-apis/register-application)). Grant it Azure Storage (user_impersonation) permission. Also, assign the 'Microsoft Sentinel Contributor' role to the application in the appropriate subscription.**

**STEP 3 - Deploy the connector and the associated Azure Functions**.

**4. Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Cohesity data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-Cohesity-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the parameters that you created at the previous steps
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**.
5. Click **Purchase** to deploy.

[← Back to Connectors Index](../connectors-index.md)
