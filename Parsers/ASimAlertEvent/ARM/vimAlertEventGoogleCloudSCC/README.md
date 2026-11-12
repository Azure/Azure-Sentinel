# Google Cloud Security Command Center ASIM AlertEvent Normalization Parser

ARM template for ASIM AlertEvent schema parser for Google Cloud Security Command Center.

This ASIM parser supports filtering and normalizing Google Cloud Security Command Center findings, stored in the GoogleCloudSCC table, to the ASIM Alert Event normalized schema. All finding classes are normalized except `SCC_ERROR`. `EventSubType` is derived from the finding class. AlertVerdict filtering is not supported by this source.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM AlertEvent normalization schema reference](https://aka.ms/ASimAlertEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAlertEvent/CHANGELOG/vimAlertEventGoogleCloudSCC.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FvimAlertEventGoogleCloudSCC%2FvimAlertEventGoogleCloudSCC.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FvimAlertEventGoogleCloudSCC%2FvimAlertEventGoogleCloudSCC.json)
