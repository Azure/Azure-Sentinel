# Amazon Web Services CloudFront (via Codeless Connector Framework) (Preview)

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `AwsCloudfrontCcpDefinition` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [AWS CloudFront](../solutions/aws-cloudfront.md) |
| **Collection Method** | CCF |
| **Connector Definition Files** | [AWSCloudFrontLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20CloudFront/Data%20Connectors/AWSCloudFrontLog_CCF/AWSCloudFrontLog_ConnectorDefinition.json) |

This data connector enables the integration of AWS CloudFront logs with Microsoft Sentinel to support advanced threat detection, investigation, and security monitoring. By utilizing Amazon S3 for log storage and Amazon SQS for message queuing, the connector reliably ingests CloudFront access logs into Microsoft Sentinel

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`AWSCloudFront_AccessLog_CL`](../tables/awscloudfront-accesslog-cl.md) | — | — |

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

## Additional Documentation

> 📄 *Source: [AWS CloudFront\Data Connectors\README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS CloudFront\Data Connectors\README.md)*

# AWS CloudFront Logs Integration with Microsoft Sentinel

## Overview
This guide explains how to integrate AWS CloudFront logs with Microsoft Sentinel using an AWS CloudFormation template. The template automates the deployment of necessary AWS resources to collect, process, and forward CloudFront access logs to Sentinel via S3 and SQS.

## Prerequisites
Before deploying, ensure you have:
- An AWS account with permissions to deploy CloudFormation stacks.
- An active Microsoft Sentinel Log Analytics Workspace ID.
- An existing CloudFront distribution with logging enabled or to be enabled.
- Required IAM permissions to configure AWS services (IAM, S3, SQS, CloudFront).

## CloudFormation Template
 Download Both the CloudFormation templates(Template 1: OpenID connect authentication deployment,Template 2: AWSCloudFront resources deployment) from connector UI page and deploy in your AWS environment.
1. OIDC Web Identity Provider

   The OIDC (OpenID Connect) Web Identity Provider allows AWS services to securely authenticate using an external identity provider without managing long-term credentials. The CloudFormation template configures OIDC as a trusted identity provider in AWS, enabling secure role-based access for forwarding AWS CloudFront logs to Microsoft Sentinel.
   
2. AWS CloudFront Configuration

      The AWS CloudFront Configuration template sets up logging for AWS CloudFront by creating an S3 bucket, SQS queues, and event notifications. This ensures logs are captured and forwarded to Microsoft Sentinel for monitoring and threat detection.

## CloudFormation Deployment

### Deploying the Stack
#### OIDC Web Identity
> **Note:**  
> If you have already deployed the **OIDC Web Identity Provider** for another AWS data connector in Microsoft Sentinel (e.g., VPC Flow Logs, GuardDuty, etc.), you do **not** need to deploy it again. You can safely skip this step and continue with the CloudFront configuration.
- Navigate to the [AWS CloudFormation console](https://aka.ms/awsCloudFormationLink#/stacks/create)
- Choose create stack
- Select upload a template file
- Upload the ODIC Web identity template and select next
- Provide the stack name and select next
- Submit the stack

#### AWS CloudFront Configuration

- Navigate to the [AWS CloudFormation console](https://aka.ms/awsCloudFormationLink#/stacks/create)
- Choose create stack
- Select upload a template file
- Upload the Aws CloudFront Configuration template and select next
- Enter the required parameters:
     - Provide the stack Name
     - Provide the Distribution ID of CloudFront
     - Microsoft Sentinel Workspace ID where logs to be stored
- Deploy the stack and wait for completion.
- Go to Outputs Tab in the stacks and save the output for future purpose

### Resources Created

The CloudFormation template will create:

- **One S3 bucket** to store AWS CloudFront logs.
- **One SQS queue** for S3 event notifications.
- **S3 Event Notification** to trigger messages to SQS on new log arrival.
- **IAM Role & Policy** granting Microsoft Sentinel access to the S3 bucket and SQS queue.
  
## Configuring CloudFront Logging

To enable logging for your CloudFront distribution and route logs to the S3 bucket created by the CloudFormation stack:
- Go to the **AWS CloudFront Console**.
- Select the relevant **CloudFront distribution**.
- Navigate to the **Logging** tab.
-  Under **Standard log destinations**, click **Add** and choose **Amazon S3**.
-   In the **S3 bucket** field, enter the bucket name provisioned by the CloudFormation stack (e.g., `aws-cloudfront-logs-<BucketName>`)
-   Expand **Additional settings**:
   - Set **Output format** to **Plain-text**.
   - Set **Field delimiter** to `\t` (tab).
- Click **Save changes** to apply the configuration.

> 📌 This ensures that CloudFront logs are written to the correct S3 bucket and in a format compatible with Microsoft Sentinel ingestion.

## Configuring Microsoft Sentinel

- Go to **Microsoft Sentinel** in the Azure Portal
- Navigate to **Content Hub > Amazon Web Services CloudFront** data connector
- Click **Connect**
- Provide the required details:
  - **IAM Role ARN** (from the CloudFormation stack output)
  - **SQS Queue URL** (from the stack output)
- Complete the setup

## Verifying Logs in Sentinel

- Go to **Microsoft Sentinel > Logs**
- Run the following Kusto Query Language (KQL) query:
  ```kql
  AWSCloudFront_AccessLog_CL
  | where TimeGenerated > ago(1h)

[← Back to Connectors Index](../connectors-index.md)
