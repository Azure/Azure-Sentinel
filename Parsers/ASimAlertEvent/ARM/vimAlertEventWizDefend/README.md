# Wiz Defend ASIM AlertEvent Normalization Parser

ARM template for ASIM AlertEvent schema parser for Wiz Defend.

This ASIM parser supports filtering and normalizing Wiz Defend threat detection events, stored in the WizDetectionsV3_CL table, to the ASIM Alert Event normalized schema. Wiz Defend is Wiz's cloud threat detection and response (TDR) capability. Detections originating from WIZ and WIZ_SENSOR (third party sources like AWS GuardDuty are filtered out) sources are all normalized under this parser. AlertVerdict filtering is not supported by this source.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM AlertEvent normalization schema reference](https://aka.ms/ASimAlertEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAlertEvent/CHANGELOG/vimAlertEventWizDefend.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FvimAlertEventWizDefend%2FvimAlertEventWizDefend.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FvimAlertEventWizDefend%2FvimAlertEventWizDefend.json)
