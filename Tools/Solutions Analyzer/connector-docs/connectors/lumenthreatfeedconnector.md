# Lumen Defender Threat Feed Data Connector

| | |
|----------|-------|
| **Connector ID** | `LumenThreatFeedConnector` |
| **Publisher** | Lumen Technologies, Inc. |
| **Tables Ingested** | [`ThreatIntelIndicators`](../tables-index.md#threatintelindicators) |
| **Used in Solutions** | [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md) |
| **Connector Definition Files** | [LumenThreatFeedConnector_ConnectorUI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Data%20Connectors/LumenThreatFeed/LumenThreatFeedConnector_ConnectorUI.json) |

The [Lumen Defender Threat Feed](https://bll-analytics.mss.lumen.com/analytics) connector provides the capability to ingest STIX-formatted threat intelligence indicators from Lumen's Black Lotus Labs research team into Microsoft Sentinel. The connector automatically downloads and uploads daily threat intelligence indicators including IPv4 addresses and domains to the ThreatIntelIndicators table via the STIX Objects Upload API.

## Permissions

**Resource Provider Permissions:**
- **Log Analytics Workspace** (Workspace): Read and write permissions on the Log Analytics workspace are required.

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Azure Entra App Registration**: An Azure Entra application registration with the Microsoft Sentinel Contributor role assigned is required for STIX Objects API access. [See the documentation to learn more about Azure Entra applications](https://docs.microsoft.com/azure/active-directory/develop/quickstart-register-app).
- **Microsoft Sentinel Contributor Role**: Microsoft Sentinel Contributor role is required for the Azure Entra application to upload threat intelligence indicators.
- **Lumen Defender Threat Feed API Key**: A Lumen Defender Threat Feed API Key is required for accessing threat intelligence data. [Contact Lumen for API access](mailto:DefenderThreatFeedSales@Lumen.com?subject=API%20Access%20Request).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions with Durable Functions to connect to the Lumen Defender Threat Feed API and upload threat intelligence indicators to Microsoft Sentinel via the STIX Objects API. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

**1. Configuration**

**STEP 1 - Obtain Lumen Defender Threat Feed API Key**

1. [Contact Lumen](mailto:DefenderThreatFeedSales@Lumen.com?subject=API%20Access%20Request) to obtain API access to our Threat Feed API service
2. Obtain your API key for authentication.

**STEP 2 - Configure Azure Entra ID Application and gather information**

1. Create an Entra application. [See the documentation for a guide to registering an application in Microsoft Entra ID.](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app)
2. Create a client secret and note the Application ID, Tenant ID, and Client Secret
4. Assign the **Microsoft Sentinel Contributor** role to the application on your Microsoft Sentinel Log Analytics Workspace
5. Make note of your Workspace ID, as well as the App Insights Workspace Resource ID, which can be obtained from the overview page of the Log Analytics Workspace for your Microsoft Sentinel instance. Click on the “JSON View” link in the top right and the Resource ID will be displayed at the top with a copy button.
- **Tenant ID**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**STEP 3 - Enable the Threat Intelligence Upload Indicators API (Preview) data connector in Microsoft Sentinel**

1. Deploy the **Threat Intelligence (New) Solution**, which includes the **Threat Intelligence Upload Indicators API (Preview)**
2. Browse to the Content Hub, find and select the **Threat Intelligence (NEW)** solution.
3. Select the **Install/Update** button.

**STEP 4 - Deploy the Azure Function**

**IMPORTANT:** Before deploying the Lumen Defender Threat Feed connector, have the Tenant ID, Workspace ID, App Insights Workspace Resource ID, Azure Entra application details (Client ID, Client Secret), and Lumen API key readily available.

1. Click the Deploy to Azure button.

[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FLumen%20Defender%20Threat%20Feed%2FData%2520Connectors%2FLumenThreatFeed%2Fazuredeploy_Connector_LumenThreatFeed_AzureFunction.json)

2. Fill in the appropriate values for each parameter:

- Subscription: Confirm the correct subscription is selected or use the dropdown to change your selection
- Resource Group: Select the resource group to be used by the Function App and related resources
- Function Name: Enter a globally unique name with an 11-character limit. Adhere to your organization’s naming convention and ensure the name is globally unique since it is used (along with the uniqueString() function) to identify the ARM template being deployed.
- Workspace ID: Found in the "Overview" tab for the Log Analytics Workspace of the Microsoft Sentinel instance and provided for convenience on the connector information page.
- Lumen API Key: Obtain an API key through Lumen support
- Lumen Base URL: Filled in automatically and should generally not be changed. This URL contains API endpoints used by the connector
- Tenant ID: Obtained from the Entra App Registration overview page for the registered application (listed as Directory ID) and can also be obtained from the Tenant Information page in Azure
- Client ID: Obtained from the Entra App Registration overview page for the registered application (listed as Application ID)
- Client Secret: Obtained when the secret is created during the app registration process. It can only be viewed when first created and is hidden permanently afterwards. Rerun the app registration process to obtain a new Client Secret if necessary.
- App Insights Workspace Resource ID: Obtained from the overview page of the Log Analytics Workspace for your Microsoft Sentinel instance. Click on the "JSON View" link in the top right and the Resource ID will be displayed at the top with a copy button.
- Blob Container Name: Use the default name unless otherwise required. Azure Blob Storage is used for temporary storage and processing of threat indicators.

**STEP 5 - Verify Deployment**

1. The connector polls for indicator updates every 15 minutes.
2. Monitor the Function App logs in the Azure Portal to verify successful execution
3. After the app performs its first run, review the indicators ingested by either viewing the “Lumen Defender Threat Feed Overview” workbook or viewing the “Threat Intelligence” section in Microsoft Sentinel. In Microsoft Sentinel “Threat Intelligence”, filter for source “Lumen” to display only Lumen generated indicators.

[← Back to Connectors Index](../connectors-index.md)
