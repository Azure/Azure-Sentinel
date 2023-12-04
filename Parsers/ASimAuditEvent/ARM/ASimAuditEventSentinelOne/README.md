# SentinelOne ASIM AuditEvent Normalization Parser

ARM template for ASIM AuditEvent schema parser for SentinelOne.

This ASIM parser supports normalizing SentinelOne logs to the ASIM Audit Event normalized schema. SentinelOne events are captured through SentinelOne data connector which ingests SentinelOne server objects such as Threats, Agents, Applications, Activities, Policies, Groups, and more events into Microsoft Sentinel through the REST API.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM AuditEvent normalization schema reference](https://aka.ms/ASimAuditEventDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuditEvent%2FARM%2FASimAuditEventSentinelOne%2FASimAuditEventSentinelOne.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuditEvent%2FARM%2FASimAuditEventSentinelOne%2FASimAuditEventSentinelOne.json)
