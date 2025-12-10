# Varonis SaaS

| | |
|----------|-------|
| **Connector ID** | `VaronisSaaS` |
| **Publisher** | Varonis |
| **Tables Ingested** | [`VaronisAlerts_CL`](../tables-index.md#varonisalerts_cl) |
| **Used in Solutions** | [VaronisSaaS](../solutions/varonissaas.md) |
| **Connector Definition Files** | [VaronisSaaS_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS/Data%20Connectors/VaronisSaaS_API_FunctionApp.json) |

Varonis SaaS provides the capability to ingest [Varonis Alerts](https://www.varonis.com/products/datalert) into Microsoft Sentinel.



Varonis prioritizes deep data visibility, classification capabilities, and automated remediation for data access. Varonis builds a single prioritized view of risk for your data, so you can proactively and systematically eliminate risk from insider threats and cyberattacks.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to Varonis DatAlert service to pull alerts into Microsoft Sentinel. This might result in additional data ingestion costs. See the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

**For Azure function and related services installation use:**

 [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVaronisSaaS%2FData%2520Connectors%2Fazuredeploy.json)

STEP 1 - Obtain the Varonis DatAlert Endpoint API credentials.

 To generate the Client ID and API key:
 1. Launch the Varonis Web Interface.
 2. Navigate to Configuration -> API Keys. The API Keys page is displayed.
 3. Click Create API Key. The Add New API Key settings are displayed on the right.
 4. Fill in the name and description.
 5. Click the Generate Key button.
 6. Copy the API key secret and  save it in a handy location. You won't be able to copy it again.

For additional information, please check: [Varonis Documentation](https://help.varonis.com/s/document-item?bundleId=ami1661784208197&topicId=emp1703144742927.html&_LANG=enus)

STEP 2 - Deploy the connector and the associated Azure Function.
- **Workspace Name**: `WorkspaceName`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

Use this method for automated deployment of the data connector using an ARM Template.

1. Click the Deploy to Azure button. 

	[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVaronisSaaS%2FData%2520Connectors%2Fazuredeploy.json)
2. Select the preferred Subscription, Resource Group, Region, Storage Account Type.
3. Enter Log Analytics Workspace Name, Varonis FQDN, Varonis SaaS API Key.
4. Click Review + Create, Create.

[← Back to Connectors Index](../connectors-index.md)
