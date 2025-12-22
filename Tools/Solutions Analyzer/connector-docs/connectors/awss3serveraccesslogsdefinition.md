# AWS S3 Server Access Logs (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `AwsS3ServerAccessLogsDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AWSS3ServerAccess`](../tables-index.md#awss3serveraccess) |
| **Used in Solutions** | [AWS_AccessLogs](../solutions/aws-accesslogs.md) |
| **Connector Definition Files** | [AWSS3ServerAccessLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_AccessLogs/Data%20Connectors/AwsS3ServerAccessLogsDefinition_CCP/AWSS3ServerAccessLogs_ConnectorDefinition.json) |

This connector allows you to ingest AWS S3 Server Access Logs into Microsoft Sentinel. These logs contain detailed records for requests made to S3 buckets, including the type of request, resource accessed, requester information, and response details. These logs are useful for analyzing access patterns, debugging issues, and ensuring security compliance.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Environment**: You must have the following AWS resources defined and configured: S3 Bucket, Simple Queue Service (SQS), IAM roles and permissions policies.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

### 1. AWS CloudFormation Deployment 
 To configure access on AWS, two templates has been generated to set up the AWS environment to send logs from an AWS S3 Server Access logs to your Log Analytics Workspace.

#### Deploy CloudFormation Templates in AWS: 
1. Navigate to the [AWS CloudFormation Stacks](https://aka.ms/awsCloudFormationLink#/stacks/create).
2. Click **Create stack** and select **With new resources**.
3. Choose **Upload a template file**, then click **Choose file** to upload the appropriate CloudFormation template provided.
4. Follow the prompts and click **Next** to complete the stack creation.
5. After the stacks are created, note down the **Role ARN** and **SQS Queue URL**.

- **Template 1: OpenID Connect authentication provider deployment**: `Oidc`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Template 2: AWS Server Access resources deployment**: `AWSS3ServerAccess`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
### 2. Connect new collectors 
 To enable AWS S3 Server Access Logs Connector for Microsoft Sentinel, click the Add new collector button, fill the required information in the context pane and click on Connect.
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Role ARN**
- **Queue URL**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add new collector**

*AWS Server Access Logs connector*

When you click the "Add new collector" button in the portal, a configuration form will open. You'll need to provide:

*Account details*

- **Role ARN** (required)
- **Queue URL** (required)

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
