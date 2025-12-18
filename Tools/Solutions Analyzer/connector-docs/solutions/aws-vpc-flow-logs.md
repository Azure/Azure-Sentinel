# AWS VPC Flow Logs

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-07-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20VPC%20Flow%20Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20VPC%20Flow%20Logs) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Amazon Web Services S3 VPC Flow Logs](../connectors/awss3vpcflowlogsparquetdefinition.md)

**Publisher:** Microsoft

This connector allows you to ingest AWS VPC Flow Logs, collected in AWS S3 buckets, to Microsoft Sentinel. AWS VPC Flow Logs provide visibility into network traffic within your AWS Virtual Private Cloud (VPC), enabling security analysis and network monitoring.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### 1. AWS CloudFormation Deployment 
 To configure access on AWS, two templates have been generated to set up the AWS environment to send VPC Flow Logs from an S3 bucket to your Log Analytics Workspace.
 #### For each template, create a Stack in AWS: 
 1. Go to [AWS CloudFormation Stacks](https://aka.ms/awsCloudFormationLink#/stacks/create). 
 2. Choose the ‘Specify template’ option, then ‘Upload a template file’ by clicking on ‘Choose file’ and selecting the appropriate CloudFormation template file provided below. Click ‘Choose file’ and select the downloaded template. 
 3. Click 'Next' and 'Create stack'.
- **Template 1: OpenID connect authentication deployment**: `Oidc`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Template 2: AWS VPC Flow Logs resources deployment**: `AwsVPCFlow`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Connect new collectors 
 To enable AWS S3 for Microsoft Sentinel, click the 'Add new collector' button, fill in the required information and click on 'Connect'
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Role ARN**
- **Queue URL**
- **File Format**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add new controller**

*AWS VPC Flow Logs connector*

When you click the "Add new collector" button in the portal, a configuration form will open. You'll need to provide:

*Account details*

- **Role ARN** (required)
- **Queue URL** (required)
- **Data type** (required): Select from available options
  - JSON Format
  - Parquet Format
  - CSV Format

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

| | |
|--------------------------|---|
| **Tables Ingested** | `AWSVPCFlow` |
| **Connector Definition Files** | [AWSVPCFlowLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20VPC%20Flow%20Logs/Data%20Connectors/AWSVPCFlowLogs_CCP/AWSVPCFlowLogs_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/awss3vpcflowlogsparquetdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AWSVPCFlow` | [Amazon Web Services S3 VPC Flow Logs](../connectors/awss3vpcflowlogsparquetdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
