# Amazon Web Services S3

| | |
|----------|-------|
| **Connector ID** | `AwsS3` |
| **Publisher** | Amazon |
| **Tables Ingested** | [`AWSCloudTrail`](../tables-index.md#awscloudtrail), [`AWSCloudWatch`](../tables-index.md#awscloudwatch), [`AWSGuardDuty`](../tables-index.md#awsguardduty), [`AWSVPCFlow`](../tables-index.md#awsvpcflow) |
| **Used in Solutions** | [Amazon Web Services](../solutions/amazon-web-services.md) |
| **Connector Definition Files** | [template_AwsS3.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Data%20Connectors/template_AwsS3.json) |

This connector allows you to ingest AWS service logs, collected in AWS S3 buckets, to Microsoft Sentinel. The currently supported data types are: 

* AWS CloudTrail

* VPC Flow Logs

* AWS GuardDuty

* AWSCloudWatch



For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2218883&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission.

**Custom Permissions:**
- **Environment**: you must have the following AWS resources defined and configured: S3, Simple Queue Service (SQS), IAM roles and permissions policies, and the AWS services whose logs you want to collect.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Set up your AWS environment**

There are two options for setting up your AWS environment to send logs from an S3 bucket to your Log Analytics Workspace:
**Setup with PowerShell script (recommended)**
  Download and extract the files from the following link: [AWS S3 Setup Script](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/AWS-S3/ConfigAwsS3DataConnectorScripts.zip).

> 1. Make sure that you have PowerShell on your machine: [Installation instructions for PowerShell](https://docs.microsoft.com/powershell/scripting/install/installing-powershell?view=powershell-7.2).

> 2. Make sure that you have the AWS CLI on your machine: [Installation instructions for the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).

Before running the script, run the aws configure command from your PowerShell command line, and enter the relevant information as prompted. See [AWS Command Line Interface | Configuration basics](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) for details. Note: When Aws configure is run, Default output format should not be set to None. It must be set to some value, such as json.
  
**Government Cloud:**
  Download and extract the files from the following link: [AWS S3 Setup Script](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/AWS-S3/ConfigAwsS3DataConnectorScriptsGov.zip).

> 1. Make sure that you have PowerShell on your machine: [Installation instructions for PowerShell](https://docs.microsoft.com/powershell/scripting/install/installing-powershell?view=powershell-7.2).

> 2. Make sure that you have the AWS CLI on your machine: [Installation instructions for the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).

Before running the script, run the aws configure command from your PowerShell command line, and enter the relevant information as prompted. See [AWS Command Line Interface | Configuration basics](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) for details. Note: When Aws configure is run, Default output format should not be set to None. It must be set to some value, such as json.
  - **Run script to set up the environment**: `./ConfigAwsConnector.ps1`
  - **External ID (Workspace ID)**: `WorkspaceId`
    > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

  **Manual Setup**

  Follow the instruction in the following link to set up the environment: [Connect AWS S3 to Microsoft Sentinel](https://aka.ms/AWSS3Connector)

**2. Add connection**
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `AwsS3`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
