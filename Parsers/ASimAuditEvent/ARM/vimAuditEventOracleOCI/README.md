# Oracle Cloud Infrastructure ASIM AuditEvent Normalization Parser

ARM template for ASIM AuditEvent schema parser for Oracle Cloud Infrastructure.

This ASIM filtering parser supports normalizing and filtering Oracle Cloud Infrastructure (OCI) API audit events, stored in the OCI_LogsV2_CL table, to the ASIM AuditEvent schema.
Excludes authentication events (handled by vimAuthenticationOracleOCI) and VCN flow log rows (handled by the OCI ASIM NetworkSession parser).


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM AuditEvent normalization schema reference](https://aka.ms/ASimAuditEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuditEvent/CHANGELOG/vimAuditEventOracleOCI.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuditEvent%2FARM%2FvimAuditEventOracleOCI%2FvimAuditEventOracleOCI.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuditEvent%2FARM%2FvimAuditEventOracleOCI%2FvimAuditEventOracleOCI.json)
