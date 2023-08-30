# CrowdStrike Data connector based on CLv2 ingestion

This connector uses Azure Functions to connect to the AWS SQS / S3 to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

## Prerequisites

1. Configure FDR in CrowdStrike - You must contact the [CrowdStrike support team](https://supportportal.crowdstrike.com/) to enable CrowdStrike FDR.		
    1. Once CrowdStrike FDR is enabled,  from the CrowdStrike console, navigate to Support --> API Clients and Keys.
	2. You need to Create new credentials to copy the AWS Access Key ID, AWS Secret Access Key, SQS Queue URL and AWS Region. 
2.  Register AAD application - For DCR to authentiate to ingest data into log analytics, you must use AAD application.
	1. [Follow the instructions here](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#create-azure-ad-application) (steps 1-5) to get **AAD Tenant Id**, **AAD Client Id** and **AAD Client Secret**. 
	2. For **AAD Principal** Id of this application, access the AAD App through [AAD Portal](https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/StartboardApplicationsMenuBlade/~/AppAppsPreview/menuId/) and capture Object Id from the application overview page.

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-CrowdstrikeReplicatorV2-azuredeploy) 
