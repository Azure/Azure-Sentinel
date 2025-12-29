# Illumio Saas

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `IllumioSaasCCFDefinition` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [IllumioSaaS](../solutions/illumiosaas.md) |
| **Collection Method** | CCF |
| **Connector Definition Files** | [IllumioSaasLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Data%20Connectors/IllumioSaasLogs_ccf/IllumioSaasLogs_ConnectorDefinition.json) |

The Illumio Saas Cloud data connector provides the capability to ingest Flow logs into Microsoft Sentinel using the Illumio Saas Log Integration through AWS S3 Bucket. Refer to [Illumio Saas Log Integration](https://product-docs-repo.illumio.com/Tech-Docs/CloudSecure/out/en/administer-cloudsecure/connector.html#UUID-c14edaab-9726-1f23-9c4c-bc2937be39ee_section-idm234556433515698) for more information.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`IllumioFlowEventsV2_CL`](../tables/illumiofloweventsv2-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Illumio Saas to Microsoft Sentinel**
>**NOTE:** This connector fetches the Illumio Saas Flow logs from AWS S3 bucket
To gather data from Illumio, you need to configure the following resources
#### 1. AWS Role ARN 
 To gather data from Illumio, you'll need AWS Role ARN.
#### 2. AWS SQS Queue URL 
 To gather data from Illumio, you'll need AWS SQS Queue URL.


For detailed steps to retrieve the AWS Role ARN, SQS Queue URL, and configure Illumio log forwarding to the Amazon S3 bucket, refer to the [Connector Setup Guide](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Data%20Connectors/IllumioSaasLogs_ccf/Readme.md).
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **AWS Role ARN**
- **AWS SQS Queue URL**
- **Table Name**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add Account**

*Add Account*

When you click the "Add Account" button in the portal, a configuration form will open. You'll need to provide:

- **Role ARN** (optional): Enter Role ARN
- **Flow Log Queue URL** (optional): Enter Flow log SQL Queue URL

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

## Additional Documentation

> 📄 *Source: [IllumioSaaS\Data Connectors\IllumioSaasLogs_ccf\Readme.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS\Data Connectors\IllumioSaasLogs_ccf\Readme.md)*

# Integrating Illumio Saas into Microsoft Sentinel
## Table of contents
- [Introduction](#intro)
- [Prerequisites](#pre)
- [Deploy the Cloud Formation Templates](#template)
- [Configure Illumio to Forward Logs to Amazon S3](#logs)


<a name = "intro">

## Introduction
The Illumio Saas Codeless Connector for Microsoft Sentinel enables seamless integration of Illumio's Logs with Microsoft Sentinel without the need for custom code. Your Illumio logs will be forwarded to an Amazon S3 bucket, which will then be used as the source for log ingestion into Microsoft Sentinel.

<a name = "pre">

## Prerequisites
- An active **AWS account** with permissions to create:
  - IAM roles and policies
  - S3 buckets
  - SQS queues

<a name = "template">
  
## Deploy the Cloud Formation Templates
- Download the [OIDC Web Identity Provider](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Data%20Connectors/CloudFormationTemplates/OIDCWebIdProvider.json) Template and the [AWS Resource Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Data%20Connectors/CloudFormationTemplates/IllumioSaasConfig.json) Template provided in this repository.
- Open the **AWS Management Console** and navigate to the **CloudFormation** service.
- Click on **"Create stack"** and choose **"With new resources (standard)"**.
- Under the **Specify template** section, select **"Upload a template file"**, and upload the appropriate CloudFormation template (starting with the OIDC template).
- Click **Next**, provide a **Stack Name** of your choice, and review or modify the parameters as needed.
- Proceed by clicking **Next**, then **Submit** to initiate the stack creation.
- Wait until the status of the first stack (OIDC Web Identity Provider) changes to **"CREATE_COMPLETE"**.
- Once completed, repeat the same steps to deploy the second template **(AWS Resource Creation Template)** using CloudFormation.
- Upon successful stack creation, make a note of the **SQS Queue URL** and **Sentinel Role ARN** available in the CloudFormation stack outputs.

<a name = "logs">

## Configuring Illumio to Forward Logs to Amazon S3
To enable log forwarding from Illumio to an Amazon S3 bucket, follow the steps outlined below:
- Log in to your Illumio console.
- From the left-hand menu, go to `Settings` → `Cloud` → `Connector`, and select the **S3 Bucket** option.
- Click on **Connect S3 Bucket** to begin the configuration process.
- **Provide AWS Account and Bucket Information**
  - If your AWS account has already been onboarded to Illumio, select the appropriate **Account ID** and **S3 Bucket ARN** from the drop-down list.
  - If the AWS account is not yet onboarded, manually enter the **Account ID**, **S3 Bucket ARN**, and the corresponding **AWS Region**, then click **Next**.
- Use an existing Illumio service account if one is available. Otherwise, create a new service account and securely save the generated credentials.
- Click on **Create CloudFormation Stack**. This will redirect you to the AWS CloudFormation stack creation page.
  - Ensure that the AWS region selected matches the region of your S3 bucket.
  - Enter the **Illumio Service Account Secret** when prompted, then proceed to create the stack.
- After the stack has been successfully deployed, return to the Illumio console.
- Click **Save and Test Connection** to validate the integration.
- A `Connection Successful` message should confirm that the log forwarding setup is complete.
- Navigate to the **Traffic** page.
- Execute the desired query to retrieve relevant traffic logs.
- Click **Export**, then select **Export to Connector**.
- Choose **CSV** as the export format.
- Select the previously configured S3 bucket.
- Specify the export **prefix** as `IllumioFlowLogs`.
- Click **Test Connection** to verify connectivity.
- Finally, click **Save**.

Once completed, Illumio traffic data will be successfully exported to the specified S3 bucket.

[← Back to Connectors Index](../connectors-index.md)
