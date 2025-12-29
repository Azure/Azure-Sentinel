# Amazon Web Services

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [Amazon Web Services](../connectors/aws.md)

**Publisher:** Amazon

### [Amazon Web Services S3](../connectors/awss3.md)

**Publisher:** Amazon

### [Amazon Web Services S3 WAF](../connectors/awss3wafccpdefinition.md)

**Publisher:** Microsoft

This connector allows you to ingest AWS WAF logs, collected in AWS S3 buckets, to Microsoft Sentinel. AWS WAF logs are detailed records of traffic that web access control lists (ACLs) analyze, which are essential for maintaining the security and performance of web applications. These logs contain information such as the time AWS WAF received the request, the specifics of the request, and the action taken by the rule that the request matched.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### 1. AWS CloudFormation Deployment 
 To configure access on AWS, two templates has been generated to set up the AWS environment to send logs from an S3 bucket to your Log Analytics Workspace.
 #### For each template, create Stack in AWS: 
 1. Go to [AWS CloudFormation Stacks](https://aka.ms/awsCloudFormationLink#/stacks/create). 
 2. Choose the ‘Specify template’ option, then ‘Upload a template file’ by clicking on ‘Choose file’ and selecting the appropriate CloudFormation template file provided below. click ‘Choose file’ and select the downloaded template. 
 3. Click 'Next' and 'Create stack'.
- **Template 1: OpenID connect authentication deployment**: `Oidc`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Template 2: AWS WAF resources deployment**: `AwsWAF`
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

| | |
|--------------------------|---|
| **Tables Ingested** | `AWSWAF` |
| **Connector Definition Files** | [AwsS3_WAF_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Data%20Connectors/AWS_WAF_CCP/AwsS3_WAF_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/awss3wafccpdefinition.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AWSCloudTrail` | [Amazon Web Services](../connectors/aws.md), [Amazon Web Services S3](../connectors/awss3.md) |
| `AWSCloudWatch` | [Amazon Web Services S3](../connectors/awss3.md) |
| `AWSGuardDuty` | [Amazon Web Services S3](../connectors/awss3.md) |
| `AWSVPCFlow` | [Amazon Web Services S3](../connectors/awss3.md) |
| `AWSWAF` | [Amazon Web Services S3 WAF](../connectors/awss3wafccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
