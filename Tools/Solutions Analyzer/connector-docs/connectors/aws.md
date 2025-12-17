# Amazon Web Services

| | |
|----------|-------|
| **Connector ID** | `AWS` |
| **Publisher** | Amazon |
| **Tables Ingested** | [`AWSCloudTrail`](../tables-index.md#awscloudtrail) |
| **Used in Solutions** | [Amazon Web Services](../solutions/amazon-web-services.md) |
| **Connector Definition Files** | [template_AWS.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Data%20Connectors/template_AWS.json) |

Follow these instructions to connect to AWS and stream your CloudTrail logs into Microsoft Sentinel. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2218883&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect AWS cloud trail with Microsoft Sentinel​**

The connection necessitates giving Microsoft permissions to access your AWS account. To enable this, follow the instructions under [Connect AWS to Microsoft Sentinel](https://aka.ms/AWSConnector) and use these parameters when prompted:

> Data from all regions will be sent to and stored in the workspace's region.

> It takes about 5 minutes until the connection streams data to your workspace.
- **Microsoft account ID**: `MicrosoftAwsAccount`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **External ID (Workspace ID)**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `AwsCloudTrail`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
