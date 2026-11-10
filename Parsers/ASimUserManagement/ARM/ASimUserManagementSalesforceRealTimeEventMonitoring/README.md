# Salesforce Real-Time Event Monitoring ASIM UserManagement Normalization Parser

ARM template for ASIM UserManagement schema parser for Salesforce Real-Time Event Monitoring.

Normalizes PermissionSetEventStore permission-set and permission-set-group assignments as UserModified, not group membership. Assignment values map to NewPropertyValue or PreviousPropertyValue; single impacted-user identifiers map to TargetUserId, while bulk events remain one row.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM UserManagement normalization schema reference](https://aka.ms/ASimUserManagementDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimUserManagement/CHANGELOG/ASimUserManagementSalesforceRealTimeEventMonitoring.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimUserManagement%2FARM%2FASimUserManagementSalesforceRealTimeEventMonitoring%2FASimUserManagementSalesforceRealTimeEventMonitoring.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimUserManagement%2FARM%2FASimUserManagementSalesforceRealTimeEventMonitoring%2FASimUserManagementSalesforceRealTimeEventMonitoring.json)
