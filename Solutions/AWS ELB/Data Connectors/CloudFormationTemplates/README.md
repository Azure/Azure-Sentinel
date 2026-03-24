# AWS ELB Data Connector - CloudFormation Configuration Guide

To ingest AWS Elastic Load Balancing logs into Microsoft Sentinel, you need to create and configure resources on AWS. This process is facilitated using CloudFormation templates.

## List of Resources Required

* Amazon S3 Bucket
* Amazon SQS Queues (4 queues for ALB, NLB access, NLB flow, and GLB flow logs)
* AWS IAM Role with OIDC-based trust policy
* S3 Bucket Policy for log delivery
* SQS Queue Policies for S3 notifications

## Configuration Steps

1. Download both CloudFormation templates from this folder:
   - [OIDCWebIdProvider.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20ELB/Data%20Connectors/CloudFormationTemplates/OIDCWebIdProvider.json)
   - [AWSS3ELB.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20ELB/Data%20Connectors/CloudFormationTemplates/AWSS3ELB.json)

2. Go to the [AWS CloudFormation Stacks](https://console.aws.amazon.com/cloudformation/home) page.

3. Create a new stack for each template:

   - **First (optional)**, create a stack using the `OIDCWebIdProvider.json` template. **Skip this step if you already have an OIDC identity provider configured for Microsoft Sentinel in your AWS account** — you can reuse the existing one in the next step:
     1. Click on **Create stack**.
     2. Choose the **With new resources** option.
     3. Click on **Choose an existing template**, then **Upload a template file** and select the `OIDCWebIdProvider.json` file.
     4. Click **Next** and follow the prompts to create the stack.

   - **Next**, create a stack using the `AWSS3ELB.json` template:
     1. Click on **Create stack**.
     2. Choose the **With new resources** option.
     3. Click on **Choose an existing template**, then **Upload a template file** and select the `AWSS3ELB.json` file.
     4. Fill in the required parameters:
        - **BucketName**: S3 bucket name for storing load balancer logs
        - **IamRoleName**: IAM role name (must start with `OIDC_`)
        - **SentinelWorkspaceId**: Your Microsoft Sentinel Workspace ID
        - **CreateNewBucket**: Set to `true` to create a new bucket or `false` to use an existing one
     5. Click **Next** and follow the prompts to create the stack.

4. After the stacks are created, note down the following outputs from the CloudFormation stack:
   - **IAMRoleArn** - IAM role ARN for the Sentinel connector
   - **ALBSQSQueueURL** - SQS queue URL for ALB access logs
   - **NLBSQSQueueURL** - SQS queue URL for NLB access logs
   - **NLBFlowLogsSQSQueueURL** - SQS queue URL for NLB flow logs
   - **GLBFlowLogsSQSQueueURL** - SQS queue URL for GLB flow logs

5. **Post-deployment Configuration**: In the S3 bucket, create the following folders:
   - `ALBLogs/`
   - `NLBAccessLogs/`
   - `NLBFlowLogs/`
   - `GLBFlowLogs/`

6. Configure your AWS load balancers to send logs to the appropriate folders:
   - ALB access logs → `ALBLogs/`
   - NLB access logs → `NLBAccessLogs/`
   - NLB flow logs → `NLBFlowLogs/`
   - GLB flow logs → `GLBFlowLogs/`

7. In Microsoft Sentinel, navigate to the Data Connectors page and find the **Amazon Web Services Elastic Load Balancing** connector.

8. Click **Add new collector**, fill in:
   - **Role ARN**: The IAMRoleArn from the CloudFormation stack output
   - **Queue URL**: The appropriate SQS Queue URL for the log type
   - **Data type**: Select the log type (ALB Access Logs, NLB Access Logs, NLB Flow Logs, or GLB Flow Logs)

9. Click **Connect** to enable the connector.

## Table Mapping

| Log Type | S3 Folder | Sentinel Table |
|---|---|---|
| ALB access logs | `ALBLogs/` | `AWSALBAccessLogs` |
| NLB access logs | `NLBAccessLogs/` | `AWSNLBAccessLogs` |
| NLB flow logs | `NLBFlowLogs/` | `AWSELBFlowLogs` |
| GLB flow logs | `GLBFlowLogs/` | `AWSELBFlowLogs` |

> **Note:** In the `AWSELBFlowLogs` table, a column named `LogType` indicates whether a row is from NLB flow logs or GLB flow logs.

## Additional Information

For more details on configuring the AWS environment for Microsoft Sentinel, refer to the [Microsoft Sentinel AWS documentation](https://learn.microsoft.com/en-us/azure/sentinel/connect-aws-configure-environment).

For any issues or support, contact [Microsoft Support](https://support.microsoft.com).
