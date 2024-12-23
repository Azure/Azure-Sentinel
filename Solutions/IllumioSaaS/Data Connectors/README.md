# Illumio Data connector based on Logs Ingestion API

This connector uses Azure Functions to connect to the AWS SQS / S3 to pull logs into Microsoft Sentinel. 
This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

## Prerequisites

1. Ensure AWS SQS is configured for the S3 bucket from which flow and auditable event logs are going to be pulled. In case, Illumio provides bucket, please contact Illumio support for sqs url, s3 bucket name and aws credentials.

2. Register AAD application - For DCR (Data collection rule) to authentiate to ingest data into log analytics, you must use Entra application.
	1. [Follow the instructions here](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#create-azure-ad-application) (steps 1-5) to get **AAD Tenant Id**, **AAD Client Id** and **AAD Client Secret**. 
	2. For **AAD Principal** Id of this application, access the AAD App through [AAD Portal](https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/StartboardApplicationsMenuBlade/~/AppAppsPreview/menuId/) and capture Object Id from the application overview page.

3. Ensure you have created a log analytics workspace. Please keep note of the name and region where it has been deployed.

## Deployment:

1. To set up the function app, follow the next steps.


### ARM Deployment of function app, data collection rules, data collection endpoint and custom tables

Use the following template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-IllumioSaaS-FunctionApp) 

### To deploy additional function apps, use the following link, note this deploys QueueTrigger function only. There is no need to deploy additional TimedApi/TimedSQS/QueueManager apps.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-IllumioSaaS-QueueTriggerFunctionApp)