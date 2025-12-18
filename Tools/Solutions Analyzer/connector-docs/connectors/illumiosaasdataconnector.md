# Illumio SaaS

| | |
|----------|-------|
| **Connector ID** | `IllumioSaaSDataConnector` |
| **Publisher** | Illumio |
| **Tables Ingested** | [`Illumio_Auditable_Events_CL`](../tables-index.md#illumio_auditable_events_cl), [`Illumio_Flow_Events_CL`](../tables-index.md#illumio_flow_events_cl) |
| **Used in Solutions** | [IllumioSaaS](../solutions/illumiosaas.md) |
| **Connector Definition Files** | [IllumioSaaS_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Data%20Connectors/IllumioSaaS_FunctionApp.json) |

[Illumio](https://www.illumio.com/) connector provides the capability to ingest events into Microsoft Sentinel. The connector provides ability to ingest auditable and flow events from AWS S3 bucket.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **SQS and AWS S3 account credentials/permissions**: **AWS_SECRET**, **AWS_REGION_NAME**, **AWS_KEY**, **QUEUE_URL** is required.  [See the documentation to learn more about data pulling](<Replace with an entry to documentation>). If you are using s3 bucket provided by Illumio, contact Illumio support. At your request they will provide you with the AWS S3 bucket name, AWS SQS url and AWS credentials to access them.
- **Illumio API key and secret**: **ILLUMIO_API_KEY**, **ILLUMIO_API_SECRET** is required for a workbook to make connection to SaaS PCE and fetch api responses.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the AWS SQS / S3 to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**1. Prerequisites**

1. Ensure AWS SQS is configured for the s3 bucket from which flow and auditable event logs are going to be pulled. In case, Illumio provides bucket, please contact Illumio support for sqs url, s3 bucket name and aws credentials. 
 2. Register AAD application - For DCR (Data collection rule) to authentiate to ingest data into log analytics, you must use Entra application. 1. [Follow the instructions here](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#create-azure-ad-application) (steps 1-5) to get **AAD Tenant Id**, **AAD Client Id** and **AAD Client Secret**. 
 2. Ensure you have created a log analytics workspace. 
Please keep note of the name and region where it has been deployed.

**2. Deployment**

Choose one of the approaches from below options. Either use the below ARM template to deploy azure resources or deploy function app manually.

**1. Azure Resource Manager (ARM) Template**

Use this method for automated deployment of Azure resources using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-IllumioSaaS-FunctionApp) 			
2. Provide the required details such as Microsoft Sentinel Workspace, AWS credentials, Azure AD Application details and ingestion configurations 
> **NOTE:** It is recommended to create a new Resource Group for deployment of function app and associated resources.
3. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
4. Click **Purchase** to deploy.

**2. Deploy additional function apps to handle scale**

Use this method for automated deployment of additional function apps using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-IllumioSaaS-QueueTriggerFunctionApp)

**3. Manual Deployment of Azure Functions**

Deployment via Visual Studio Code.

**1. Deploy a Function App**

1. Download the [Azure Function App](https://github.com/Azure/Azure-Sentinel/raw/master/Solutions/IllumioSaaS/Data%20Connectors/IllumioEventsConn.zip) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

**2. Configure the Function App**

1. Follow documentation <insert link> to set up all required environment variables and click **Save**. Ensure you restart the function app once settings are saved.

[← Back to Connectors Index](../connectors-index.md)
