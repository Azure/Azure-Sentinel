# Illumio Data connector based on Logs Ingestion API

This connector uses Azure Functions to connect to the AWS SQS / S3 to pull logs into Microsoft Sentinel. 
This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

## Prerequisites

1. Ensure AWS SQS is configured for the S3 bucket from which flow and auditable event logs are going to be pulled. In case, Illumio provides bucket, please contact Illumio support for sqs url, s3 bucket name and aws credentials.

2. Use Managed Identity - For DCR (Data collection rule) to authenticate to ingest data into log analytics, you must use Managed Identity.
   1. For new function app deployments, the template now automatically assigns the Monitoring Metrics Publisher role to the Function App's managed identity on the Data Collection Rule.
   2. For existing function app deployments, follow the steps below to manually assign the Monitoring Metrics Publisher role.

      **Step 1: Enable Managed Identity on Function App**
      1. Navigate to Azure Portal → Function Apps → [Your Illumio Function App]
      2. In the left menu, select Settings → Identity
      3. On the System assigned tab:
         - Set Status to On
         - Click Save
         - Click Yes to confirm
      4. Copy the Object (principal) ID - you'll need this for Step 2

      **Step 2: Assign Monitoring Metrics Publisher Role to Managed Identity**
      1. Navigate to Azure Portal → Monitor → Data Collection Rules
      2. Select your Data Collection Rule (e.g., intg-dcr-illumio)
      3. In the left menu, select Access control (IAM)
      4. Click + Add → Add role assignment
      5. Configure the role assignment
      6. Click Review + assign

3. Ensure you have created a log analytics workspace. Please keep note of the name and region where it has been deployed.

## Deployment:

1. To set up the function app, follow the next steps.


### ARM Deployment of function app, data collection rules, data collection endpoint and custom tables

Use the following template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-IllumioSaaS-FunctionApp) 

### To deploy additional function apps, use the following link, note this deploys QueueTrigger function only. There is no need to deploy additional TimedApi/TimedSQS/QueueManager apps.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-IllumioSaaS-QueueTriggerFunctionApp)