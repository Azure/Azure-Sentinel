# Google SecOps ASIM AlertEvent Normalization Parser

ARM template for ASIM AlertEvent schema parser for Google SecOps.

This ASIM parser supports normalizing and filtering Google SecOps Detection Alerts
(ingested via the DetectionAlerts_CL custom table) to the ASIM AlertEvent normalized schema.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM AlertEvent normalization schema reference](https://aka.ms/ASimAlertEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAlertEvent/CHANGELOG/vimAlertEventGoogleSecOps.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FvimAlertEventGoogleSecOps%2FvimAlertEventGoogleSecOps.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FvimAlertEventGoogleSecOps%2FvimAlertEventGoogleSecOps.json)
