# CrowdStrike Falcon Data Replicator ASIM UserManagement Normalization Parser

ARM template for ASIM UserManagement schema parser for CrowdStrike Falcon Data Replicator.

Normalizes account creation, deletion, and group-membership events from CrowdStrike_User_Events_CL to ASIM UserManagement.
Maps available device and target account fields even when the current source samples leave them empty.
Actor identity and initiating client IP are unavailable and are not inferred from target usernames, agent IPs, or process identifiers.
Event timestamps use Unix milliseconds with TimeGenerated as a fallback. Each source record remains one normalized event.
Set pack=true to retain source metadata and the original AdditionalFields object under AdditionalFields.SourceAdditionalFields.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM UserManagement normalization schema reference](https://aka.ms/ASimUserManagementDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimUserManagement/CHANGELOG/ASimUserManagementCrowdStrikeFalconDataReplicator.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimUserManagement%2FARM%2FASimUserManagementCrowdStrikeFalconDataReplicator%2FASimUserManagementCrowdStrikeFalconDataReplicator.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimUserManagement%2FARM%2FASimUserManagementCrowdStrikeFalconDataReplicator%2FASimUserManagementCrowdStrikeFalconDataReplicator.json)
