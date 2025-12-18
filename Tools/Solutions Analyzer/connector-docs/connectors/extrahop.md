# ExtraHop Detections Data Connector

| | |
|----------|-------|
| **Connector ID** | `ExtraHop` |
| **Publisher** | ExtraHop |
| **Tables Ingested** | [`ExtraHop_Detections_CL`](../tables-index.md#extrahop_detections_cl) |
| **Used in Solutions** | [ExtraHop](../solutions/extrahop.md) |
| **Connector Definition Files** | [ExtraHop_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop/Data%20Connectors/ExtraHopDataConnector/ExtraHop_FunctionApp.json) |

The [ExtraHop](https://extrahop.com/) Detections Data Connector enables you to import detection data from ExtraHop RevealX to Microsoft Sentinel through webhook payloads.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Azure Subscription**: Azure Subscription with owner role is required to register an application in Microsoft Entra ID and assign role of contributor to app in resource group.
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **ExtraHop RevealX permissions**: The following is required on your ExtraHop RevealX system:
 1.Your RevealX system must be running firmware version 9.9.2 or later.
 2.Your RevealX system must be connected to ExtraHop Cloud Services.
 3.Your user account must have System Administratin privileges on RevealX 360 or Full Write privileges on RevealX Enterprise.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the ExtraHop in which logs are pushed via ExtraHop webhook and it will ingest logs into Microsoft Sentinel. Furthermore, the connector will fetch the ingested data from the custom logs table and create Threat Intelligence Indicators into Microsoft Sentinel Threat Intelligence. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias **ExtraHopDetections** and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop/Parsers/ExtraHopDetections.yaml). The function usually takes 10-15 minutes to activate after solution installation/update.

**STEP 1 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the ExtraHop Microsoft Sentinel data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following) readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Azure Resource Manager (ARM) Template**

Complete the following steps for automated deployment of the ExtraHop Detections Data Connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ExtraHop-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the values for the following parameters:

	 a. **Function Name** - Enter the Function Name you want. 

	 b. **Workspace ID** - Enter the Workspace ID of the log analytics Workspace. 

	 c. **Workspace Key** - Enter the Workspace Key of the log analytics Workspace. 

	 d. **Detections Table Name** - Enter the name of the table used to store ExtraHop detection data. 

	 e. **LogLevel** - Select Debug, Info, Error, or Warning for the log level or log severity value. 

	 f. **AppInsightsWorkspaceResourceID** - Enter the value of the 'Log Analytic Workspace-->Properties-->Resource ID' property. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Complete the following steps to manually deploy the ExtraHop Detections Data Connector with Azure Functions (Deployment via Visual Studio Code).

**5. 1) Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-ExtraHop-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. ExtraHopXXXXX).

	e. **Select a runtime:** Choose Python 3.11 or above.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**6. 2) Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with the following respective values (case-sensitive): 

	 a. **Function Name** - Enter the Function Name you want. 

	 b. **Workspace ID** - Enter the Workspace ID of the log analytics Workspace. 

	c. **Workspace Key** - Enter the Workspace Key of the log analytics Workspace. 

	d. **Detections Table Name** - Enter the name of the table used to store ExtraHop detection data. 

	e. **LogLevel** - Select Debug, Info, Error, or Warning for the log level or log severity value. 

	 f. **logAnalyticsUri (optional)** - Configure this option to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
4. Once all application settings have been entered, click **Save**.

**STEP 2 - Post Deployment**

**8. 1) Get the Function App endpoint**

1. Go to the Azure function overview page and click the **"Functions"** tab.
2. Click on the function called **"ExtraHopHttpStarter"**.
3. Go to **"GetFunctionurl"** and copy the function url available under **"default (Function key)"**.
4. Replace **{functionname}**  with **"ExtraHopDetectionsOrchestrator"** in copied function url.

**9. 2) Configure a connection to Microsoft Sentinel and specify webhook payload criteria from RevealX**

From your ExtraHop system, configure the Microsoft Sentinel integration to establish a connection between Microsoft Sentinel and ExtraHop RevealX and to create detection notification rules that will send webhook data to Microsoft Sentinel. For detailed instructions, refer to [Integrate ExtraHop RevealX with Microsoft Sentinel SIEM](https://docs.extrahop.com/current/integrations-microsoft-sentinel-siem/).

*After notification rules have been configured and Microsoft Sentinel is receiving webhook data, the Function App is triggered and you can view ExtraHop detections from the Log Analytics workspace table named "ExtraHop_Detections_CL".*

[← Back to Connectors Index](../connectors-index.md)
