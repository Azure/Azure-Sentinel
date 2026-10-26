# CrowdStrike Falcon Data Replicator ASIM AuditEvent Normalization Parser

ARM template for ASIM AuditEvent schema parser for CrowdStrike Falcon Data Replicator.

Normalizes CrowdStrike_Audit_Events_CL to the ASIM Audit Event schema, including
configuration, policy, account, file, share, and device audit operations.
Only event_simpleName identifies operations; records with an empty value are excluded.
Unknown event names map to Other. Undocumented numeric enumerations are retained
without guessing their meanings. Missing device or object values remain empty.
Use pack=true to retain original source fields, including currently empty columns.
The source-IP prefix parameter in the filtering parser supports IPv4 prefixes.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM AuditEvent normalization schema reference](https://aka.ms/ASimAuditEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuditEvent/CHANGELOG/ASimAuditEventCrowdStrikeFalconDataReplicator.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuditEvent%2FARM%2FASimAuditEventCrowdStrikeFalconDataReplicator%2FASimAuditEventCrowdStrikeFalconDataReplicator.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuditEvent%2FARM%2FASimAuditEventCrowdStrikeFalconDataReplicator%2FASimAuditEventCrowdStrikeFalconDataReplicator.json)
