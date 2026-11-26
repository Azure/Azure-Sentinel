# AWS CloudTrail ASIM AuditEvent Normalization Parser

ARM template for ASIM AuditEvent schema parser for AWS CloudTrail.

Filters and normalizes AWSCloudTrail events from ec2.amazonaws.com for EC2 Fleets, Spot Fleets, Spot
requests, Spot pricing and placement scores, and Spot datafeed subscriptions. This
parser is referenced by vimAuditEventAWSCloudTrail.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM AuditEvent normalization schema reference](https://aka.ms/ASimAuditEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuditEvent/CHANGELOG/vimAuditEventAWSCloudTrailEC2FleetAndSpot.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuditEvent%2FARM%2FvimAuditEventAWSCloudTrailEC2FleetAndSpot%2FvimAuditEventAWSCloudTrailEC2FleetAndSpot.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuditEvent%2FARM%2FvimAuditEventAWSCloudTrailEC2FleetAndSpot%2FvimAuditEventAWSCloudTrailEC2FleetAndSpot.json)
