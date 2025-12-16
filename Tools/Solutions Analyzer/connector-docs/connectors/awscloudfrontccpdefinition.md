# Amazon Web Services CloudFront (via Codeless Connector Framework) (Preview)

| | |
|----------|-------|
| **Connector ID** | `AwsCloudfrontCcpDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AWSCloudFront_AccessLog_CL`](../tables-index.md#awscloudfront_accesslog_cl) |
| **Used in Solutions** | [AWS CloudFront](../solutions/aws-cloudfront.md) |
| **Connector Definition Files** | [AWSCloudFrontLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20CloudFront/Data%20Connectors/AWSCloudFrontLog_CCF/AWSCloudFrontLog_ConnectorDefinition.json) |

This data connector enables the integration of AWS CloudFront logs with Microsoft Sentinel to support advanced threat detection, investigation, and security monitoring. By utilizing Amazon S3 for log storage and Amazon SQS for message queuing, the connector reliably ingests CloudFront access logs into Microsoft Sentinel

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Ingesting AWS CloudFront logs in Microsoft Sentinel**

### List of Resources Required:

* Open ID Connect (OIDC) web identity provider
* IAM Role
* Amazon S3 Bucket
* Amazon SQS
* AWS CloudFront configuration
#### 1. AWS CloudFormation Deployment 
 To configure access on AWS, two templates has been generated to set up the AWS environment to send logs from an S3 bucket to your Log Analytics Workspace.
 #### For each template, create Stack in AWS: 
 1. Go to [AWS CloudFormation Stacks](https://aka.ms/awsCloudFormationLink#/stacks/create). 
 2. Choose the ‘**Specify template**’ option, then ‘**Upload a template file**’ by clicking on ‘**Choose file**’ and selecting the appropriate CloudFormation template file provided below. click ‘**Choose file**’ and select the downloaded template. 
 3. Click '**Next**' and '**Create stack**'.
- **Template 1: OpenID connect authentication deployment**: `Oidc`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Template 2: AWSCloudFront resources deployment**: `AWSCloudFront`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Connect new collectors 
 To enable AWS S3 for Microsoft Sentinel, click the Add new collector button, fill the required information in the context pane and click on Connect.
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Role ARN**
- **Queue URL**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add new controller**

*AWS S3 connector*

When you click the "Add new collector" button in the portal, a configuration form will open. You'll need to provide:

*Account details*

- **Role ARN** (required)
- **Queue URL** (required)

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
