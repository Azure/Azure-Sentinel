
# AWS S3 Microsoft Sentinel Connector
AWS S3 Sentinel Connector is a connector that allows you to bring many AWS logs to Azure Sentinel currently supported AWS VPC Flow Logs, GuardDuty, Cloud Trail (Management and Data events). To make this work, you need to set up multiple resources and permissions.
We have created several PowerShell scripts to ease the onboarding and set up these resources automatically.

please use the following command to execute the scripts: .\ConfigAwsConnector.ps1

# Script pre requirements 
* PowerShell [Installation instructions](https://docs.microsoft.com/powershell/scripting/install/installing-powershell?view=powershell-7.1)
* AWS CLI [Installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
