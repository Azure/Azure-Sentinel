# Salesforce Service Cloud ASIM Authentication Normalization Parser

ARM template for ASIM Authentication schema parser for Salesforce Service Cloud.

This ASIM parser supports filtering and normalizing Salesforce Service Cloud authentication logs stored in the 'SalesforceServiceCloudV2_CL' table to the ASIM Authentication normalized schema. It supports filtering by time range, username, target app name, source IP, event type, event result details, and event result.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM Authentication normalization schema reference](https://aka.ms/ASimAuthenticationDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/CHANGELOG/vimAuthenticationSalesforceServiceCloudV2.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuthentication%2FARM%2FvimAuthenticationSalesforceServiceCloudV2%2FvimAuthenticationSalesforceServiceCloudV2.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuthentication%2FARM%2FvimAuthenticationSalesforceServiceCloudV2%2FvimAuthenticationSalesforceServiceCloudV2.json)
