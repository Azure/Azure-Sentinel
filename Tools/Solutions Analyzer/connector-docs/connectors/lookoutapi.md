# [DEPRECATED] Lookout

| | |
|----------|-------|
| **Connector ID** | `LookoutAPI` |
| **Publisher** | Lookout |
| **Tables Ingested** | [`Lookout_CL`](../tables-index.md#lookout_cl) |
| **Used in Solutions** | [Lookout](../solutions/lookout.md) |
| **Connector Definition Files** | [Lookout_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Data%20Connectors/Lookout_API_FunctionApp.json) |

The [Lookout](https://lookout.com) data connector provides the capability to ingest [Lookout](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide#commoneventfields) events into Microsoft Sentinel through the Mobile Risk API. Refer to [API documentation](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide) for more information. The [Lookout](https://lookout.com) data connector provides ability to get events which helps to examine potential security risks and more.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Mobile Risk API Credentials/permissions**: **EnterpriseName** & **ApiKey** are required for Mobile Risk API. [See the documentation to learn more about API](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide). Check all [requirements and follow  the instructions](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide#authenticatingwiththemobileriskapi) for obtaining credentials.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This [Lookout](https://lookout.com) data connector uses Azure Functions to connect to the Mobile Risk API to pull its events into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**LookoutEvents**](https://aka.ms/sentinel-lookoutapi-parser) which is deployed with the Microsoft Sentinel Solution.

**STEP 1 - Configuration steps for the Mobile Risk API**

 [Follow the instructions](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide#authenticatingwiththemobileriskapi) to obtain the credentials.

**STEP 2 - Follow below mentioned instructions to deploy the [Lookout](https://lookout.com) data connector and the associated Azure Function**

>**IMPORTANT:** Before starting the deployment of the [Lookout](https://lookout.com) data connector, make sure to have the Workspace ID and Workspace Key ready (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Workspace Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Azure Resource Manager (ARM) Template**

Follow below steps for automated deployment of the [Lookout](https://lookout.com) data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-lookoutapi-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Region**. 
> **NOTE:** Within the same resource group, you can't mix Windows and Linux apps in the same region. Select existing resource group without Windows apps in it or create new resource group.
3. Enter the **Function Name**, **Workspace ID**,**Workspace Key**,**Enterprise Name** & **Api Key** and deploy. 
4. Click **Create** to deploy.

[← Back to Connectors Index](../connectors-index.md)
