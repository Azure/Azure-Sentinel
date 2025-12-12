# VMware SD-WAN and SASE Connector

| | |
|----------|-------|
| **Connector ID** | `VMwareSDWAN` |
| **Publisher** | VMware by Broadcom |
| **Tables Ingested** | [`VMware_CWS_DLPLogs_CL`](../tables-index.md#vmware_cws_dlplogs_cl), [`VMware_CWS_Health_CL`](../tables-index.md#vmware_cws_health_cl), [`VMware_CWS_Weblogs_CL`](../tables-index.md#vmware_cws_weblogs_cl), [`VMware_VECO_EventLogs_CL`](../tables-index.md#vmware_veco_eventlogs_cl) |
| **Used in Solutions** | [VMware SD-WAN and SASE](../solutions/vmware-sd-wan-and-sase.md) |
| **Connector Definition Files** | [VMwareSASE_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Data%20Connectors/Function%20App%20Connector/VMwareSASE_API_FunctionApp.json) |

The [VMware SD-WAN & SASE](https://sase.vmware.com) data connector offers the capability to ingest VMware SD-WAN and CWS events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developer.vmware.com/apis/vmware-sase-platform/) for more information. The connector provides ability to get events which helps to examine potential network security issues, identify misconfigured network devices and monitor SD-WAN and SASE usage. If you have your own custom connector, make sure that the connector is deployed under an isolated Log Analytics Workspace first. In case of issues, questions or feature requests, please contact us via email on sase-siem-integration@vmware.com.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **api_veco_authorization**, **api_veco_fqdn** is required for REST API. [See the documentation to learn more about VMware SASE APIs](https://developer.vmware.com/apis/vmware-sase-platform/). Check all [requirements and follow  the instructions](https://docs.vmware.com/en/VMware-SD-WAN/5.3/VMware-SD-WAN-Administration-Guide/GUID-2FA3763F-835C-4D10-A32B-450FEB5397D8.html) for obtaining credentials. The Function App only supports token-based API authentication. Be advised that the API Token generated will inherit the access rights of the user account under which it was generated.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the VMware Edge Cloud Orchestrator REST API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

**STEP 1 - Configuration steps for the VECO API**

 [Follow the instructions](https://docs.vmware.com/en/VMware-SD-WAN/5.3/VMware-SD-WAN-Administration-Guide/GUID-2FA3763F-835C-4D10-A32B-450FEB5397D8.html) to create and obtain the credentials.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function.**

**3. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the VMware SD-WAN and SASE Connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinelvmwaresdwan)
2. Select the preferred **Subscription**, **Resource Group** and **Location**.
3. Enter or modify the Function App, Log Analytics and Azure Monitor settings, enter the VECO FQDN (without https://, for example vco123-usvi1.velocloud.net), enter the API token created (including "Token " at the beginning of the string), and adjust your desired Function App freaquency, then deploy. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the VMware SD-WAN and SASE Connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-vmwaresdwan-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. vmwsase-siemXXXXXXXXXXXXX).

	e. **Select a runtime:** Choose Python 3.10.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab .
3. Check if the application has these settings defined correctly and adjust if needed: 
		api_veco_authorization
		api_veco_fqdn
		app_frequency_mins
		azsa_share_connectionstring
		azsa_share_name dce_endpoint
		dcr_cwsdlplog_immutableid
		dcr_cwshealth_immutableid
		dcr_cwsweblog_immutableid
		dcr_efsfwlog_immutableid
		dcr_efshealth_immutableid
		dcr_saseaudit_immutableid
		stream_cwsdlplog
		stream_cwshealth
		stream_cwsweblog
		stream_efsfwlog
		stream_efshealth
		stream_saseaudit
3. In case you made changes to application settings have been entered, make sure that you click **Save**.

[← Back to Connectors Index](../connectors-index.md)
