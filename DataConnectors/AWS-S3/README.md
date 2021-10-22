# AWS S3 Microsoft Sentinel Connector

## Introduction

AWS S3 Sentinel connector ingests many AWS service logs into Azure Sentinel. Currently supported logs include: AWS VPC Flow Logs, GuardDuty, Cloud Trail (management and data events). 

This connector requires that each AWS service publish its logs to an S3 bucket in your account. In addition you must configure SQS notifications and permissions for the connector to retreive the logs.

More information on the connector and configuration instructions can be found on the Azure Sentinel data connector page in the Azure portal.

## Configuration process

This set of PowerShell scripts can be used to automatically configure the necessary resources.

At a high level, these scripts do the following:

1. Create an AWS assumed role and grant access to the AWS Sentinel account.
2. Configure the AWS service (VPC Flow Logs/GuardDuty) to export gzipped logs to an S3 bucket.
3. Create a standard Simple Queue Service (SQS) in AWS.
4. Enable SQS notification.
5. Grant the Sentinel AWS account access to the S3 bucket & SQS.

## Script prerequisites

You must have PowerShell and the AWS CLI installed before using these scripts.

- PowerShell [Installation instructions](https://docs.microsoft.com/powershell/scripting/install/installing-powershell?view=powershell-7.1)
- AWS CLI [Installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)

## Using the scripts

Download the scripts in this folder and subfolders or download and extract the `ConfigAwsS3DataConnectorScripts.zip` file to your computer. 
Make sure that you have PowerShell and the AWS CLI installed.

Then run the following from PowerShell and follow the prompts to complete the configuration.

```powershell

.\ConfigAwsConnector.ps1

```

When the script(s) complete, you must complete the Azure Sentinel data connector configuration in the Azure portal.

## Troubleshooting

By default, a log is created in the directory where the script is executed.