# Amazon Web Services Route 53

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-03-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20Route%2053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20Route%2053) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Amazon Web Services S3 DNS Route53 (via Codeless Connector Framework)](../connectors/awsroute53resolverccpdefinition.md)

**Publisher:** Microsoft

This connector enables ingestion of AWS Route 53 DNS logs into Microsoft Sentinel for enhanced visibility and threat detection. It supports DNS Resolver query logs ingested directly from AWS S3 buckets, while Public DNS query logs and Route 53 audit logs can be ingested using Microsoft Sentinel's AWS CloudWatch and CloudTrail connectors. Comprehensive instructions are provided to guide you through the setup of each log type. Leverage this connector to monitor DNS activity, detect potential threats, and improve your security posture in cloud environments.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. AWS Route53**

This connector enables the ingestion of AWS Route 53 DNS logs into Microsoft Sentinel, providing enhanced visibility into DNS activity and strengthening threat detection capabilities. It supports direct ingestion of DNS Resolver query logs from AWS S3 buckets, while Public DNS query logs and Route 53 audit logs can be ingested via Microsoft Sentinel’s AWS CloudWatch and CloudTrail connectors. Detailed setup instructions are provided for each log type. Use this connector to monitor DNS traffic, identify potential threats, and enhance your cloud security posture.

You can ingest the following type of logs from AWS Route 53 to Microsoft Sentinel:
1. Route 53 Resolver query logs
2. Route 53 Public Hosted zones query logs (via Microsoft Sentinel CloudWatch connector)
3. Route 53 audit logs (via Microsoft Sentinel CloudTrail connector)

**Ingesting Route53 Resolver query logs in Microsoft Sentinel**

  ### List of Resources Required:

* Open ID Connect (OIDC) web identity provider
* IAM Role
* Amazon S3 Bucket
* Amazon SQS
* Route 53 Resolver query logging configuration
* VPC to associate with Route53 Resolver query log config
  #### 1. AWS CloudFormation Deployment 
 To configure access on AWS, two templates has been generated to set up the AWS environment to send logs from an S3 bucket to your Log Analytics Workspace.
 #### For each template, create Stack in AWS: 
 1. Go to [AWS CloudFormation Stacks](https://aka.ms/awsCloudFormationLink#/stacks/create). 
 2. Choose the ‘**Specify template**’ option, then ‘**Upload a template file**’ by clicking on ‘**Choose file**’ and selecting the appropriate CloudFormation template file provided below. click ‘**Choose file**’ and select the downloaded template. 
 3. Click '**Next**' and '**Create stack**'.
  - **Template 1: OpenID connect authentication deployment**: `Oidc`
    > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
  - **Template 2: AWS Route53 resources deployment**: `AWSRoute53Resolver`
    > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
  ### 2. Connect new collectors 
 To enable Amazon Web Services S3 DNS Route53 for Microsoft Sentinel, click the Add new collector button, fill the required information in the context pane and click on Connect.
  **Connector Management Interface**

  This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

  📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
  - **Role ARN**
  - **Queue URL**

  ➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

  🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

  > 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

  **Add new controller**

  *AWS Security Hub connector*

  When you click the "Add new collector" button in the portal, a configuration form will open. You'll need to provide:

  *Account details*

  - **Role ARN** (required)
  - **Queue URL** (required)

  > 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.


  **Ingesting Route 53 Public Hosted zones query logs (via Microsoft Sentinel CloudWatch connector)**

  Public Hosted zone query logs are exported to CloudWatch service in AWS. We can use 'Amazon Web Services S3' connector to ingest CloudWatch logs from AWS to Microsoft Sentinel.
**Step 1: Configure logging for Public DNS queries**

    1. Sign in to the AWS Management Console and open the Route 53 console at [AWS Route 53](https://console.aws.amazon.com/route53/).
2. Navigate to Route 53 > Hosted zones.
3. Choose the Public hosted zone that you want to configure query logging for.
4. In the Hosted zone details pane, click "Configure query logging".
5. Choose an existing log group or create a new log group.
6. Choose Create.

    **Step 2: Configure Amazon Web Services S3 data connector for AWS CloudWatch**

    AWS CloudWatch logs can be exported to an S3 bucket using lambda function. To ingest Public DNS queries from `AWS CloudWatch` to `S3` bucket and then to Microsoft Sentinel, follow the instructions provided in the [Amazon Web Services S3 connector](https://learn.microsoft.com/en-us/azure/sentinel/connect-aws?tabs=s3).

  **Ingesting Route 53 audit logs (via Microsoft Sentinel CloudTrail connector)**

  Route 53 audit logs i.e. the logs related to actions taken by user, role or AWS service in Route 53 can be exported to an S3 bucket via AWS CloudTrail service. We can use 'Amazon Web Services S3' connector to ingest CloudTrail logs from AWS to Microsoft Sentinel.
**Step 1: Configure logging for AWS Route 53 Audit logs**

    1. Sign in to the AWS Management Console and open the CloudTrail console at [AWS CloudTrail](https://console.aws.amazon.com/cloudtrail)
2. If you do not have an existing trail, click on 'Create trail'
3. Enter a name for your trail in the Trail name field.
4. Select Create new S3 bucket (you may also choose to use an existing S3 bucket).
5. Leave the other settings as default, and click Next.
6. Select Event type, make sure Management events is selected.
7. Select API activity, 'Read' and 'Write'
8. Click Next.
9. Review the settings and click 'Create trail'.

    **Step 2: Configure Amazon Web Services S3 data connector for AWS CloudTrail**

    To ingest audit and management logs from  `AWS CloudTrail` to Microsoft Sentinel, follow the instructions provided in the [Amazon Web Services S3 connector](https://learn.microsoft.com/en-us/azure/sentinel/connect-aws?tabs=s3)

| | |
|--------------------------|---|
| **Tables Ingested** | `AWSRoute53Resolver` |
| **Connector Definition Files** | [AWSRoute53Resolver_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20Route%2053/Data%20Connectors/AWSRoute53Resolver_CCP/AWSRoute53Resolver_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/awsroute53resolverccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AWSRoute53Resolver` | [Amazon Web Services S3 DNS Route53 (via Codeless Connector Framework)](../connectors/awsroute53resolverccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
