# AWS GuardDuty ASIM NetworkSession Normalization Parser

ARM template for ASIM NetworkSession schema parser for AWS GuardDuty.

This ASIM parser supports normalizing AWS GuardDuty findings that carry network context (service.action.networkConnectionAction or service.action.awsApiCallAction) to the ASIM Network Session normalized schema. Findings are ingested through the Microsoft Sentinel AWS S3 connector into the AWSGuardDuty table; findings without network context (for example, pure S3 policy or EKS control-plane findings) are filtered out by this parser and are better served by AssumedRole/S3/EKS-specific content.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM NetworkSession normalization schema reference](https://aka.ms/ASimNetworkSessionDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/CHANGELOG/ASimNetworkSessionAWSGuardDuty.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimNetworkSession%2FARM%2FASimNetworkSessionAWSGuardDuty%2FASimNetworkSessionAWSGuardDuty.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimNetworkSession%2FARM%2FASimNetworkSessionAWSGuardDuty%2FASimNetworkSessionAWSGuardDuty.json)
