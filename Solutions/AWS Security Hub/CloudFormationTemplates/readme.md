# AWS Security Hub Findings Data Connector Configuration Guide

To ingest data into Microsoft Sentinel, we need to create and configure few resources on AWS. This process will be facilitated using CloudFormation templates.

### List of Resources Required

* Web Identity Provider
* Amazon EventBridge
* Amazon Data Firehose
* Amazon S3 Bucket
* Amazon SQS

### Configuration Steps

1. Download both the CloudFormation Templates in this folder:
   - [OIDCWebIdProvider.json](OIDCWebIdProvider.json)
   - [SecurityHubResourcesAndConfig.json](SecurityHubResourcesAndConfig.json)

2. Go to the [AWS CloudFormation Stacks](https://console.aws.amazon.com/cloudformation/home) page.

3. Create a new stack for each template:
   - First, create a stack using the `OIDCWebIdProvider.json` template:
     1. Click on "Create stack".
     2. Choose the "Specify template" option.
     3. Click on "Upload a template file" and select the `OIDCWebIdProvider.json` file.
     4. Click "Next" and follow the prompts to create the stack.

   - Next, create a stack using the `SecurityHubResourcesAndConfig.json` template:
     1. Click on "Create stack".
     2. Choose the "Specify template" option.
     3. Click on "Upload a template file" and select the `SecurityHubResourcesAndConfig.json` file.
     4. Click "Next" and follow the prompts to create the stack.

4. After the stacks are created, note down the following outputs from the CloudFormation stack:
   - Role ARN
   - SQS Queue URL

5. In Microsoft Sentinel, navigate to the Data Connectors page and find the AWS Security Hub Findings connector.

6. Click on "Add new collector" and fill in the required information:
   - Role ARN: Enter the Role ARN obtained from the CloudFormation stack.
   - Queue URL: Enter the SQS Queue URL obtained from the CloudFormation stack.

7. Click "Connect" to enable the AWS Security Hub Findings connector.

### Additional Information

For more details on connecting data sources, refer to the [Microsoft Sentinel documentation](https://docs.microsoft.com/azure/sentinel/connect-data-sources).

For any issues or support, contact [Microsoft Support](https://support.microsoft.com).