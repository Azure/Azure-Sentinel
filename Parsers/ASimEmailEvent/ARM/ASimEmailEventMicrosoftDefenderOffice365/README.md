# Microsoft Defender for Office 365 ASIM EmailEvent Normalization Parser

ARM template for ASIM EmailEvent schema parser for Microsoft Defender for Office 365.

Normalizes native EmailEvents delivery records into ASIM EmailEvent 1.0.0.
Successful delivery does not establish that a message is safe.
Created following the official ASIM parser creation skill files directly, with documented query-only validation adaptations.
Validated against 1,636 workspace EmailEvents records using query-local execution.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM EmailEvent normalization schema reference](https://aka.ms/ASimEmailEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimEmailEvent/CHANGELOG/ASimEmailEventMicrosoftDefenderOffice365.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FASimEmailEventMicrosoftDefenderOffice365%2FASimEmailEventMicrosoftDefenderOffice365.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FASimEmailEventMicrosoftDefenderOffice365%2FASimEmailEventMicrosoftDefenderOffice365.json)
