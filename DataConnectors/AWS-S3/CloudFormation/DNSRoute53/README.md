# Amazon Web Services DNS Route53 Data Connector Configuration Guide

This connector enables the ingestion of AWS Route 53 DNS logs into Microsoft Sentinel, providing enhanced visibility into DNS activity and strengthening threat detection capabilities. It supports direct ingestion of DNS Resolver query logs from AWS S3 buckets, while Public DNS query logs and Route 53 audit logs can be integrated via Microsoft Sentinel’s AWS CloudWatch and CloudTrail connectors. Detailed setup instructions are provided for each log type. Use this connector to monitor DNS traffic, identify potential threats, and enhance your cloud security posture.

You can ingest the following type of logs from AWS Route 53 to Microsoft Sentinel:
1. Route 53 Resolver query logs
2. Route 53 Public Hosted zones query logs (via Microsoft Sentinel CloudWatch connector)
3. Route 53 audit logs (via Microsoft Sentinel CloudTrail connector)

## 1. Ingesting Route53 Resolver query logs in Microsoft Sentinel

### List of Resources Required:

* Open ID Connect (OIDC) web identity provider
* IAM Role
* Amazon S3 Bucket
* Amazon SQS
* Route 53 Resolver query logging configuration
* VPC to associate with Route53 Resolver query log config

### Configuration Steps:

1. Download the CloudFormation templates provided below:
   - [OIDCWebIdProvider.json](https://github.com/Azure/Azure-Sentinel/blob/c1344c7c13a718f771f444a54e51a3962a6dbbbd/DataConnectors/AWS-S3/CloudFormation/OIDCWebIdProvider.json): Template to configure the OIDC Web Identity Provider.
   - [AWSRoute53ResolverLogs_CloudFormation.json](https://github.com/Azure/Azure-Sentinel/blob/c1344c7c13a718f771f444a54e51a3962a6dbbbd/DataConnectors/AWS-S3/CloudFormation/DNSRoute53/AWSRoute53ResolverLogs_CloudFormation.json): Template to deploy Route53 resources and configurations.
2. Go to the [AWS CloudFormation Stacks](https://console.aws.amazon.com/cloudformation/home) page. Make sure to select the right AWS region where you want all resources need to be created.
3. Create a new Stack for each template:
   - First, create Stack using the `OIDCWebIdProvider.json` template:
     1. Click on "Create Stack".
     2. Choose the "With new resources (standard)" option.
     3. Click on "Choose an existing template", "Upload a template file" and select the `OIDCWebIdProvider.json` file.
     4. Click "Next" and follow the prompts to create the Stack.
   - Next, create another Stack using the `AWSRoute53ResolverLogs_CloudFormation.json` template:
     1. Click on "Create Stack".
     2. Choose the "With new resources (standard)" option.
     3. Click on "Choose an existing template", "Upload a template file" and select the `AWSRoute53ResolverLogs_CloudFormation.json` file.
     4. Click "Next" and follow the prompts to create the Stack.
     5. After the Stack is successfully deployed, note down the 'Value' for the following 'Key's from the Stack 'Outputs' tab:
        - `SentinelRoleArn`
        - `SentinelSQSQueueURL`
4. In the Azure portal, navigate to Microsoft Sentinel > Data Connectors, and search for the `Amazon Web Services S3 DNS Route53` data connector.
5. Click on "Add new collector" and fill in the required information:
   - `Role ARN`: Enter the Role ARN obtained from the CloudFormation stack.
   - `Queue URL`: Enter the SQS Queue URL obtained from the CloudFormation stack.
6. Click "Connect" to start ingesting logs to your Sentinel Workspace.

## 2. Ingesting Route 53 Public Hosted zones query logs (via Microsoft Sentinel CloudWatch connector)
Public Hosted zone query logs are exported to CloudWatch service in AWS. We can use 'Amazon Web Services S3' connector to ingest CloudWatch logs from AWS to Microsoft Sentinel.

### Step 1: Configure logging for Public DNS queries

1. Sign in to the AWS Management Console and open the Route 53 console at [AWS Route 53](https://console.aws.amazon.com/route53/).
2. Navigate to Route 53 > Hosted zones.
3. Choose the Public hosted zone that you want to configure query logging for.
4. In the Hosted zone details pane, click "Configure query logging".
5. Choose an existing log group or create a new log group.
6. Choose Create.
### Step 2: Configure Amazon Web Services S3 data connector for AWS CloudWatch
AWS CloudWatch logs can be exported to an S3 bucket using lambda function. To ingest Public DNS queries from `AWS CloudWatch` to `S3` bucket and then to Microsoft Sentinel, follow the instructions provided in the [Amazon Web Services S3 connector](https://learn.microsoft.com/en-us/azure/sentinel/connect-aws?tabs=s3).

## 3. Ingesting Route 53 audit logs (via Microsoft Sentinel CloudTrail connector)

Route 53 audit logs i.e. the logs related to actions taken by user, role or AWS service in Route 53 can be exported to an S3 bucket via AWS CloudTrail service. We can use 'Amazon Web Services S3' connector to ingest CloudTrail logs from AWS to Microsoft Sentinel.

### Step 1: Configure logging for AWS Route 53 Audit logs:

1. Sign in to the AWS Management Console and open the CloudTrail console at [AWS CloudTrail](https://console.aws.amazon.com/cloudtrail)
2. If you do not have an existing trail, click on 'Create trail'
3. Enter a name for your trail in the Trail name field.
4. Select Create new S3 bucket (you may also choose to use an existing S3 bucket).
5. Leave the other settings as default, and click Next.
6. Select Event type, make sure Management events is selected.
7. Select API activity, 'Read' and 'Write'
8. Click Next.
9. Review the settings and click 'Create trail'.

### Step 2: Configure Amazon Web Services S3 data connector for AWS CloudTrail
To ingest audit and management logs from  `AWS CloudTrail` to Microsoft Sentinel, follow the instructions provided in the [Amazon Web Services S3 connector](https://learn.microsoft.com/en-us/azure/sentinel/connect-aws?tabs=s3)