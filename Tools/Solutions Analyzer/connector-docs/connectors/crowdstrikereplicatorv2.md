# CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)

| | |
|----------|-------|
| **Connector ID** | `CrowdstrikeReplicatorv2` |
| **Publisher** | Crowdstrike |
| **Tables Ingested** | [`ASimAuditEventLogs`](../tables-index.md#asimauditeventlogs), [`ASimAuthenticationEventLogs`](../tables-index.md#asimauthenticationeventlogs), [`ASimAuthenticationEventLogs_CL`](../tables-index.md#asimauthenticationeventlogs_cl), [`ASimDnsActivityLogs`](../tables-index.md#asimdnsactivitylogs), [`ASimFileEventLogs`](../tables-index.md#asimfileeventlogs), [`ASimFileEventLogs_CL`](../tables-index.md#asimfileeventlogs_cl), [`ASimNetworkSessionLogs`](../tables-index.md#asimnetworksessionlogs), [`ASimProcessEventLogs`](../tables-index.md#asimprocesseventlogs), [`ASimProcessEventLogs_CL`](../tables-index.md#asimprocesseventlogs_cl), [`ASimRegistryEventLogs`](../tables-index.md#asimregistryeventlogs), [`ASimRegistryEventLogs_CL`](../tables-index.md#asimregistryeventlogs_cl), [`ASimUserManagementActivityLogs`](../tables-index.md#asimusermanagementactivitylogs), [`ASimUserManagementLogs_CL`](../tables-index.md#asimusermanagementlogs_cl), [`CrowdStrike_Additional_Events_CL`](../tables-index.md#crowdstrike_additional_events_cl), [`CrowdStrike_Secondary_Data_CL`](../tables-index.md#crowdstrike_secondary_data_cl) |
| **Used in Solutions** | [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md) |
| **Connector Definition Files** | [CrowdstrikeReplicatorV2_ConnectorUI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdstrikeReplicatorCLv2/CrowdstrikeReplicatorV2_ConnectorUI.json) |

This connector enables the ingestion of FDR data into Microsoft Sentinel using Azure Functions to support the assessment of potential security risks, analysis of collaboration activities, identification of configuration issues, and other operational insights.<p><span style='color:red; font-weight:bold;'>NOTE:</span></p><div style='margin-left:20px;'><p>1. CrowdStrike FDR license must be available & enabled.</p><p>2. The connector uses a Key & Secret based authentication and is suitable for CrowdStrike Managed buckets.</p><p>3. For environments that use a fully owned AWS S3 bucket, Microsoft recommends using the <strong>CrowdStrike Falcon Data Replicator (AWS S3)</strong> connector.</p></div>

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **SQS and AWS S3 account credentials/permissions**: **AWS_SECRET**, **AWS_REGION_NAME**, **AWS_KEY**, **QUEUE_URL** is required.  [See the documentation to learn more about data pulling](https://www.crowdstrike.com/blog/tech-center/intro-to-falcon-data-replicator/). To start, contact CrowdStrike support. At your request they will create a CrowdStrike managed Amazon Web Services (AWS) S3 bucket for short term storage purposes as well as a SQS (simple queue service) account for monitoring changes to the S3 bucket.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the AWS SQS / S3 to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**1. Prerequisites**

1. Configure FDR in CrowdStrike - You must contact the [CrowdStrike support team](https://supportportal.crowdstrike.com/) to enable CrowdStrike FDR.
	 - Once CrowdStrike FDR is enabled,  from the CrowdStrike console, navigate to Support --> API Clients and Keys. 
	 - You need to Create new credentials to copy the AWS Access Key ID, AWS Secret Access Key, SQS Queue URL and AWS Region. 
2.  Register AAD application - For DCR to authentiate to ingest data into log analytics, you must use AAD application. 
	 - [Follow the instructions here](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#create-azure-ad-application) (steps 1-5) to get **AAD Tenant Id**, **AAD Client Id** and **AAD Client Secret**. 
	 - For **AAD Principal** Id of this application, access the AAD App through [AAD Portal](https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/StartboardApplicationsMenuBlade/~/AppAppsPreview/menuId/) and capture Object Id from the application overview page.

**2. Deployment Options**

Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function

**3. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Crowdstrike Falcon Data Replicator connector V2 using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-CrowdstrikeReplicatorV2-azuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-CrowdstrikeReplicatorV2-azuredeploy-gov) 			
2. Provide the required details such as Microsoft Sentinel Workspace, CrowdStrike AWS credentials, Azure AD Application details and ingestion configurations 
> **NOTE:** Within the same resource group, you can't mix Windows and Linux apps in the same region. Select existing resource group without Windows apps in it or create new resource group. It is recommended to create a new Resource Group for deployment of function app and associated resources.
3. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
4. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Crowdstrike Falcon Data Replicator connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy DCE, DCR and Custom Tables for data ingestion**

1. Deploy the required DCE,  DCR(s) and the Custom Tables by using the [Data Collection Resource ARM template](https://aka.ms/sentinel-CrowdstrikeReplicatorV2-azuredeploy-data-resource) 
2. After successful deployment of DCE and DCR(s), get the below information and keep it handy (required during Azure Functions app deployment).
	 - DCE log ingestion - Follow the instructions available at [Create data collection endpoint](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#create-data-collection-endpoint) (Step 3).
	 - Immutable Ids of one or more DCRs (as applicable) - Follow the instructions available at [Collect information from the DCR](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#collect-information-from-the-dcr) (Stpe 2).

**2. Deploy a Function App**

1. Download the [Azure Function App](https://aka.ms/sentinel-CrowdstrikeReplicatorV2-functionapp) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

**3. Configure the Function App**

1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Configuration**.
3. In the **Application settings** tab, select ** New application setting**.
4. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		AWS_KEY
		AWS_SECRET
		AWS_REGION_NAME
		QUEUE_URL
		USER_SELECTION_REQUIRE_RAW //True if raw data is required
		USER_SELECTION_REQUIRE_SECONDARY //True if secondary data is required
		MAX_QUEUE_MESSAGES_MAIN_QUEUE // 100 for consumption and 150 for Premium
		MAX_SCRIPT_EXEC_TIME_MINUTES // add the value of 10 here
		AZURE_TENANT_ID
		AZURE_CLIENT_ID
		AZURE_CLIENT_SECRET
		DCE_INGESTION_ENDPOINT
		NORMALIZED_DCR_ID
		RAW_DATA_DCR_ID
		EVENT_TO_TABLE_MAPPING_LINK // File is present on github. Add if the file can be accessed using internet
		REQUIRED_FIELDS_SCHEMA_LINK //File is present on github. Add if the file can be accessed using internet
		Schedule //Add value as '0 */1 * * * *' to ensure the function runs every minute.
5. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
