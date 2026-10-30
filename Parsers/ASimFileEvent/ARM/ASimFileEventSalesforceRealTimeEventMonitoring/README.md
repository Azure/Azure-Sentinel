# Salesforce Real-Time Event Monitoring ASIM FileEvent Normalization Parser

ARM template for ASIM FileEvent schema parser for Salesforce Real-Time Event Monitoring.

Normalizes documented API_DOWNLOAD, UI_DOWNLOAD, PREVIEW, and UPLOAD actions. FileName is used without inventing a path; API_DOWNLOAD rows without FileName can produce an empty TargetFilePath and require review. Upload is mapped conservatively, and transfer success is not inferred.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM FileEvent normalization schema reference](https://aka.ms/ASimFileEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimFileEvent/CHANGELOG/ASimFileEventSalesforceRealTimeEventMonitoring.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimFileEvent%2FARM%2FASimFileEventSalesforceRealTimeEventMonitoring%2FASimFileEventSalesforceRealTimeEventMonitoring.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimFileEvent%2FARM%2FASimFileEventSalesforceRealTimeEventMonitoring%2FASimFileEventSalesforceRealTimeEventMonitoring.json)
