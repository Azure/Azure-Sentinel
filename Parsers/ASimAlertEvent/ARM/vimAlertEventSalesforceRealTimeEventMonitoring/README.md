# Salesforce Real-Time Event Monitoring ASIM AlertEvent Normalization Parser

ARM template for ASIM AlertEvent schema parser for Salesforce Real-Time Event Monitoring.

Salesforce anomaly event-store records are normalized as alert events. The source does not supply analyst verdicts or normalized severity, so verdict and severity defaults are conservative; source score remains additional context. Identity-provider and LoginAccessChange coverage are not included.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM AlertEvent normalization schema reference](https://aka.ms/ASimAlertEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAlertEvent/CHANGELOG/vimAlertEventSalesforceRealTimeEventMonitoring.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FvimAlertEventSalesforceRealTimeEventMonitoring%2FvimAlertEventSalesforceRealTimeEventMonitoring.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAlertEvent%2FARM%2FvimAlertEventSalesforceRealTimeEventMonitoring%2FvimAlertEventSalesforceRealTimeEventMonitoring.json)
