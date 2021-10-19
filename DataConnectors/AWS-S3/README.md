
# AWS S3 Microsoft Sentinel Connector
AWS S3 Sentinel connector allows you to bring many AWS logs to Azure Sentinel. Currently supported logs include: AWS VPC Flow Logs, GuardDuty, Cloud Trail (Management and Data events). 
Before configuring the connector, you need to create multiple resources and set appropriate permissions.

This set of PowerShell scripts can be used to automatically configure the necessary resources.

# Script prerequisites
You must have PowerShell and the AWS CLI installed before using these scripts.

- PowerShell [Installation instructions](https://docs.microsoft.com/powershell/scripting/install/installing-powershell?view=powershell-7.1)
- AWS CLI [Installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)

# Using the scripts
Download all scripts in this folder and subfolders to your computer with PowerShell and the AWS CLI installed.

Then run the following from PowerShell and follow the prompts to complete the configuration.

```powershell

.\ConfigAwsConnector.ps1

```
