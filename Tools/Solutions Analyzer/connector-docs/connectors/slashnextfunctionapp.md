# SlashNext Function App

| | |
|----------|-------|
| **Connector ID** | `SlashNextFunctionApp` |
| **Publisher** | SlashNext |
| **Used in Solutions** | [SlashNext](../solutions/slashnext.md) |
| **Connector Definition Files** | [SlashNext_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext/Data%20Connectors/SlashNext_FunctionApp.json) |

The SlashNext function app utilizes python to perform the analysis of the raw logs and returns URLs present in the logs.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | — | ✗ |
| [`AzureMetrics`](../tables/azuremetrics.md) | ✗ | ✗ |

## Permissions

**Resource Provider Permissions:**
- **Storage Account** (Storage Account): read, write, and delete permissions on the storage account are required.

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Microsoft.Web/serverfarms permissions**: Read and write permissions to Azure App Service Plan are required to create and manage the App Service Plan. [See the documentation to learn more about App Service Plans](https://learn.microsoft.com/azure/app-service/overview-hosting-plans).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Custom Deployment Using Azure Resource Manager (ARM) Template**

Follow these steps to perform custom deployment of the SlashNext function app using ARM template:

1. Click this [link](https://portal.azure.com/#create/Microsoft.Template) to open the Microsoft Azure Portal for custom deployment.
2. Under the **Select a template** tab in the **Custom deployment** section, click **Build your own template in the editor**.
3. Copy the contents of the **azuredeploy.json ARM template file** from this [GitHub repository](https://github.com/MuhammadAli-snx/Azure-Sentinel/blob/master/Solutions/SlashNext/FunctionApp/azuredeploy.json) and paste them into the **Edit template** section.
4. Click the **Save** button.
5. Select the preferred **Subscription**, **Resource Group**, and **Location**.
6. Click **Create** to deploy.

[← Back to Connectors Index](../connectors-index.md)
