# Salesforce Real-Time Event Monitoring ASIM Authentication Normalization Parser

ARM template for ASIM Authentication schema parser for Salesforce Real-Time Event Monitoring.

This ASIM filtering parser normalizes Salesforce Real-Time Event Monitoring authentication events (LoginEvent, LoginAsEvent, LogoutEvent and IdentityVerificationEvent) stored in the SalesForceRealTimeEventMonitoring_CL table to the ASIM Authentication schema.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM Authentication normalization schema reference](https://aka.ms/ASimAuthenticationDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/CHANGELOG/vimAuthenticationSalesforceRealTimeEventMonitoring.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuthentication%2FARM%2FvimAuthenticationSalesforceRealTimeEventMonitoring%2FvimAuthenticationSalesforceRealTimeEventMonitoring.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuthentication%2FARM%2FvimAuthenticationSalesforceRealTimeEventMonitoring%2FvimAuthenticationSalesforceRealTimeEventMonitoring.json)
