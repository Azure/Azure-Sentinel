# Amazon Web Services NetworkFirewall (via Codeless Connector Framework)

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `AwsNetworkFirewallCcpDefinition` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [Amazon Web Services NetworkFirewall](../solutions/amazon-web-services-networkfirewall.md) |
| **Collection Method** | CCF |
| **Connector Definition Files** | [AWSNetworkFirewallLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20NetworkFirewall/Data%20Connectors/AWSNetworkFirewallLogs_CCP/AWSNetworkFirewallLog_ConnectorDefinition.json) |

This data connector allows you to ingest AWS Network Firewall logs into Microsoft Sentinel for advanced threat detection and security monitoring. By leveraging Amazon S3 and Amazon SQS, the connector forwards network traffic logs, intrusion detection alerts, and firewall events to Microsoft Sentinel, enabling real-time analysis and correlation with other security data

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`AWSNetworkFirewallAlert`](../tables/awsnetworkfirewallalert.md) | — | ✗ |
| [`AWSNetworkFirewallFlow`](../tables/awsnetworkfirewallflow.md) | — | ✗ |
| [`AWSNetworkFirewallTls`](../tables/awsnetworkfirewalltls.md) | — | ✗ |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Ingesting AWS NetworkFirewall logs in Microsoft Sentinel**

### List of Resources Required:

* Open ID Connect (OIDC) web identity provider
* IAM Role
* Amazon S3 Bucket
* Amazon SQS
* AWSNetworkFirewall configuration
* Follow this instructions for [AWS NetworkFirewall Data connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20NetworkFirewall/Data%20Connectors/readme.md) configuration
#### 1. AWS CloudFormation Deployment 
 To configure access on AWS, two templates has been generated to set up the AWS environment to send logs from an S3 bucket to your Log Analytics Workspace.
 #### For each template, create Stack in AWS: 
 1. Go to [AWS CloudFormation Stacks](https://aka.ms/awsCloudFormationLink#/stacks/create). 
 2. Choose the ‘**Specify template**’ option, then ‘**Upload a template file**’ by clicking on ‘**Choose file**’ and selecting the appropriate CloudFormation template file provided below. click ‘**Choose file**’ and select the downloaded template. 
 3. Click '**Next**' and '**Create stack**'.
- **Template 1: OpenID connect authentication deployment**: `Oidc`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Template 2: AWSNetworkFirewall resources deployment**: `AWSNetworkFirewall`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Connect new collectors 
 To enable AWS S3 for Microsoft Sentinel, click the Add new collector button, fill the required information in the context pane and click on Connect.
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Role ARN**
- **Queue URL**
- **Stream name**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add new controller**

*AWS S3 connector*

When you click the "Add new collector" button in the portal, a configuration form will open. You'll need to provide:

*Account details*

- **Role ARN** (required)
- **Queue URL** (required)
- **Data type** (required): Select from available options
  - Alert Log
  - Flow Log
  - Tls Log

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

## Additional Documentation

> 📄 *Source: [Amazon Web Services NetworkFirewall\Data Connectors\readme.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon Web Services NetworkFirewall\Data Connectors\readme.md)*

## Overview
This guide explains how to integrate AWS Network Firewall logs with Microsoft Sentinel using an AWS CloudFormation template. The template automates the deployment of necessary resources to collect, process, and forward logs to Sentinel.

## Prerequisites
Before deploying, ensure you have:
- An AWS account with permissions to deploy CloudFormation stacks.
- An existing AWS Network Firewall setup.
- An active Microsoft Sentinel Log Analytics Workspace ID.
- Required IAM permissions to configure AWS services.

## CloudFormation Templates
 Download Both the CloudFormation templates(Template 1: OpenID connect authentication deployment,Template 2: AWS Network Firewall Configuration) from connector UI page and deploy in your AWS environment.
  
1. OpenID Connect

   The OIDC (OpenID Connect) Web Identity Provider allows AWS services to securely authenticate using an external identity provider without managing long-term credentials. The CloudFormation template configures OIDC as a trusted identity provider in AWS, enabling secure role-based access for forwarding AWS Network Firewall logs to Microsoft Sentinel.
   
2. AWS Network Firewall Configuration

      The AWS Network Firewall Configuration template sets up logging for AWS Network Firewall by creating an S3 bucket, SQS queues, and event notifications. This ensures logs are captured and forwarded to Microsoft Sentinel for monitoring and threat detection.

## CloudFormation Deployment
### Deploying the Stack
#### ODIC Web Identity
- Navigate to the [AWS CloudFormation console](https://aka.ms/awsCloudFormationLink#/stacks/create)
- Choose create stack
- Select upload a template file
- Upload the ODIC Web identity template and select next
- Provide the stack name and select next
- Submit the stack

#### AWS Network Firewall Configuration

- Navigate to the [AWS CloudFormation console](https://aka.ms/awsCloudFormationLink#/stacks/create)
- Choose create stack
- Select upload a template file
- Upload the Aws NetworkFirewall Configuration template and select next
- Enter the required parameters:
     - Provide the stack Name
     - Microsoft Sentinel Workspace ID where logs to be stored
- Deploy the stack and wait for completion.
- Go to Outputs Tab in the stacks and save the output for future purpose
### Resources Created
The CloudFormation template will create:

- One S3 bucket to store AWS Network Firewall logs.
- Three SQS queues for log processing and forwarding.
- S3 Event Notifications to trigger log forwarding.
- IAM Roles & Policies with the necessary permissions.
### Configuring AWS Network Firewall Logs
- Go to the Firewall Service, navigate to the Logging tab, and enable the log types: FLOW, ALERT, and TLS.
- Select S3 as the log destination and enter the S3 bucket name created by the CloudFormation stack.
### Configuring Microsoft Sentinel
- Navigate to microsoft sentinel
- Go to Amazon Web Services NetworkFirewall data connector
- Select Add New collector
- Provide the Required Details - Role ARN, Queue URL, Datatype
- Ensure that the ARN remains the same for all data types (Alert, Flow, and TLS), while each data type has its respective Queue URL.
## Verifying Logs in Sentinel
- Go to Log Analytics in Microsoft Sentinel.
- Run the following Kusto Query Language (KQL) query:
  - For Flow Logs
    ```
    AWSNetworkFirewallFlow
    | where TimeGenerated > ago(1h)
    ```
  - For Alert Logs
    ```
    AWSNetworkFirewallAlert
    | where TimeGenerated > ago(1h)
    ```
  - For Tls Logs
    ```
    AWSNetworkFirewallTls
    | where TimeGenerated > ago(1h)
    ```
- Ensure logs appear correctly.
## Troubleshooting
- No logs in Sentinel? Check Event Notifications in S3 Bucket to ensure the Prefix path matches the S3 bucket logs path.
- Event Notification Path
  ```
  AWS S3 Bucket -> Properties -> Event Notifications -> Select Event Notification -> Edit -> General configuration Make sure S3 bucket path and prefix path should be the same
  ```
  
- IAM permission errors? Ensure CloudFormation created the correct policies.

[← Back to Connectors Index](../connectors-index.md)
