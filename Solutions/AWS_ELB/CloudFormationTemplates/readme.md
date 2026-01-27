# AWS S3 ELB Logs Data Connector Configuration Guide

To ingest data into Microsoft Sentinel, we need to create and configure few resources on AWS. This process will be facilitated using CloudFormation templates.

### List of Resources Required

* Amazon S3 Bucket
* Amazon SQS

### Configuration Steps

1. Download both the CloudFormation Templates in this folder:
   - [OIDCWebIdProvider.json](https://github.com/Alekhya0824/GithubValidationREPO/blob/main/AWSS3ELBLogs/CloudFormationTemplates/OIDCWebIdProvider.json)
   - [AWSS3ELB.json](https://github.com/Alekhya0824/GithubValidationREPO/blob/main/AWSS3ELBLogs/CloudFormationTemplates/AWSS3ELB.json)

2. Go to the [AWS CloudFormation Stacks](https://console.aws.amazon.com/cloudformation/home) page.

3. Create a new stack for each template:
   - First, create a stack using the `OIDCWebIdProvider.json` template:
     1. Click on "Create stack".
     2. Choose the "With new resources" option.
     3. Click on "Choose an existing template", "Upload a template file" and select the `OIDCWebIdProvider.json` file.
     4. Click "Next" and follow the prompts to create the stack.

   - Next, create a stack using the `AWSS3ELB.json` template:
     1. Click on "Create stack".
     2. Choose the "With new resources" option.
     3. Click on "Choose an existing template", "Upload a template file" and select the `AWSS3ELB.json` file.
     4. Click "Next" and follow the prompts to create the stack.

4. After the stacks are created, note down the following outputs from the CloudFormation stack:
   - IAMRoleArn
   - ALBSQSQueueURL
   - NLBSQSQueueURL
   - NLBFlowLogsSQSQueueURL
   - GLBFlowLogsSQSQueueURL

5. In Microsoft Sentinel, navigate to the Data Connectors page and find the AWS Security Hub Findings connector.

6. Click on "Add new collector" and fill in the required information:
   - Role ARN: Enter the Role ARN obtained from the CloudFormation stack.
   - Queue URL: Enter the SQS Queue URL obtained from the CloudFormation stack.
   - Data Type: Select the Data type from the drop down.

7. Click "Connect" to enable the AWS Security Hub Findings connector.

### Additional Information

For more details on connecting data sources, refer to the [Microsoft Sentinel documentation](https://docs.microsoft.com/azure/sentinel/connect-data-sources).

For any issues or support, contact [Microsoft Support](https://support.microsoft.com).