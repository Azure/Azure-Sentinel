# ESET Protect Platform

| | |
|----------|-------|
| **Connector ID** | `ESETProtectPlatform` |
| **Publisher** | ESET |
| **Tables Ingested** | [`IntegrationTableIncidents_CL`](../tables-index.md#integrationtableincidents_cl), [`IntegrationTable_CL`](../tables-index.md#integrationtable_cl) |
| **Used in Solutions** | [ESET Protect Platform](../solutions/eset-protect-platform.md) |
| **Connector Definition Files** | [ESETProtectPlatform_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Protect%20Platform/Data%20Connectors/ESETProtectPlatform_API_FunctionApp.json) |

The ESET Protect Platform data connector enables users to inject detections data from [ESET Protect Platform](https://www.eset.com/int/business/protect-platform/) using the provided [Integration REST API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Protect%20Platform/Data%20Connectors). Integration REST API runs as scheduled Azure Function App.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Permission to register an application in Microsoft Entra ID**: Sufficient permissions to register an application with your Microsoft Entra tenant are required.
- **Permission to assign a role to the registered application**: Permission to assign the Monitoring Metrics Publisher role to the registered application in Microsoft Entra ID is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** The ESET Protect Platform data connector uses Azure Functions to connect to the ESET Protect Platform via Eset Connect API to pull detections logs into Microsoft Sentinel. This process might result in additional data ingestion costs. See details on the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/).

>**NOTE:** The newest version of the ESET PROTECT Platform and Microsoft Sentinel integration pulls not only detections logs but also newly created incidents. If your integration was set up before 20.06.2025, please follow [these steps](https://help.eset.com/eset_connect/en-US/update_ms_sentinel_integration.html) to update it.

**1. Step 1 -  Create an API user**

Use this [instruction](https://help.eset.com/eset_connect/en-US/create_api_user_account.html) to create an ESET Connect API User account with **Login** and **Password**.

**2. Step 2 -  Create a registered application**

Create a Microsoft Entra ID registered application by following the steps in the [Register a new application instruction.](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app)

**3. Step 3 - Deploy the ESET Protect Platform data connector using the Azure Resource Manager (ARM) template**

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-EsetProtectionPlatform-azuredeploy)

2. Select the name of the **Log Analytics workspace** associated with your Microsoft Sentinel. Select the same **Resource Group** as the Resource Group of the Log Analytics workspace.

3. Type the parameters of the registered application in Microsoft Entra ID: **Azure Client ID**, **Azure Client Secret**, **Azure Tenant ID**, **Object ID**. You can find the **Object ID** on Azure Portal by following this path 
> Microsoft Entra ID -> Manage (on the left-side menu) -> Enterprise applications -> Object ID column (the value next to your registered application name).

4. Provide the ESET Connect API user account **Login** and **Password** obtained in **Step 1**.

5. Select one or more ESET products (ESET PROTECT, ESET Inspect, ESET Cloud Office Security) from which detections are retrieved.

[← Back to Connectors Index](../connectors-index.md)
