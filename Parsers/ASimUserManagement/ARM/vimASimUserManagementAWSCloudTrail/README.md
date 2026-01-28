# AWS CloudTrail ASIM UserManagement Normalization Filter Parser

ARM template for ASIM UserManagement schema parser for AWS CloudTrail.

This ASIM filter parser supports normalizing user management activity in the AWS CloudTrail events to the ASIM User Management schema.

The parser supports the following EventSources:
- cognito-idp.amazonaws.com
- iam.amazonaws.com

The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM UserManagement normalization schema reference](https://aka.ms/ASimUserManagementDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimUserManagement%2FARM%2FvimUserManagementCiscoISE%2FvimUserManagementAWSCloudTrail.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimUserManagement%2FARM%2FvimUserManagementAWSCloudTrail%2FvimUserManagementAWSCloudTrail.json)
