# Wiz Cloud ASIM AlertEvent Normalization Parser

ARM template for ASIM AlertEvent schema parser for Wiz Cloud.

This ASIM parser supports normalizing Wiz Cloud issues, stored in the WizIssuesV3_CL table, to the ASIM Alert Event normalized schema. WizIssuesV3_CL represents Wiz's unified Issues engine, covering cloud configuration findings, control failures, toxic combinations of risk factors, and correlated threat detections. EventSubType is derived per-row: THREAT_DETECTION issues, and TOXIC_COMBINATION issues whose rule name matches a confirmed-exploit keyword list, are normalized as "Threat". All other issues (cloud configuration/posture findings, control failures, and predictive/reachability-only toxic combinations) are normalized as "Compliance Violation".


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM AlertEvent normalization schema reference](https://aka.ms/ASimAlertEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAlertEvent/CHANGELOG/ASimAlertEventWizCloud.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FASimAlertEventWizCloud%2FASimAlertEventWizCloud.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FASimAlertEventWizCloud%2FASimAlertEventWizCloud.json)
