# VMRayThreatIntelligence

| | |
|----------|-------|
| **Connector ID** | `VMRay` |
| **Publisher** | VMRay |
| **Tables Ingested** | [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [VMRay](../solutions/vmray.md) |
| **Connector Definition Files** | [VMRayThreatIntelligence_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Data%20Connectors/VMRayThreatIntelligence_FunctionApp.json) |

VMRayThreatIntelligence connector automatically generates and feeds threat intelligence for all submissions to VMRay, improving threat detection and incident response in Sentinel. This seamless integration empowers teams to proactively address emerging threats.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Azure Subscription**: Azure Subscription with owner role is required to register an application in azure active directory() and assign role of contributor to app in resource group.
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **VMRay API Key** is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the VMRay API to pull VMRay Threat IOCs into Microsoft Sentinel. This might result in additional costs for data ingestion and for storing data in Azure Blob Storage costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) and [Azure Blob Storage pricing page](https://azure.microsoft.com/pricing/details/storage/blobs/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**1. Deploy VMRay Threat Intelligence Connector**

1. Ensure you have all the required prerequisites: **Client ID**, **Tenant ID**, **Client Secret**, **VMRay API Key**, and **VMRay Base URL**.
2. To obtain the Client ID, Client Secret, and Tenant ID, [follow these instructions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/VMRay#vmray-configurations)
3. For the **Flex Consumption Plan**, click the **Deploy to Azure** button below:

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-VMRay-azuredeployflex)

4. For the **Premium Plan**, click the **Deploy to Azure** button below:

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-VMRay-azuredeploypremium).

[← Back to Connectors Index](../connectors-index.md)
