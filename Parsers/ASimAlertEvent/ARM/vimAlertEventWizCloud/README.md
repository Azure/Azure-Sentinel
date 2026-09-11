# Wiz Cloud ASIM AlertEvent Normalization Parser

ARM template for ASIM AlertEvent schema parser for Wiz Cloud.

This ASIM parser supports filtering and normalizing Wiz Cloud issues, stored in the WizIssuesV3_CL table, to the ASIM Alert Event normalized schema. This source has no IP address data or MITRE ATT&CK mapping, so `ipaddr_has_any_prefix`, `attacktactics_has_any`, and `attacktechniques_has_any` are accepted for compatibility but are not functional. `username_has_any` filters on the entity name when the issue's affected entity is an identity (USER_ACCOUNT/SERVICE_ACCOUNT). It is a not functional for resource-type entities, which have no username. AlertVerdict filtering is also not supported by this source.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM AlertEvent normalization schema reference](https://aka.ms/ASimAlertEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAlertEvent/CHANGELOG/vimAlertEventWizCloud.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FvimAlertEventWizCloud%2FvimAlertEventWizCloud.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FvimAlertEventWizCloud%2FvimAlertEventWizCloud.json)
