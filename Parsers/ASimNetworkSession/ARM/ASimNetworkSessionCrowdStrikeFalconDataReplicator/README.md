# CrowdStrike Falcon Data Replicator ASIM NetworkSession Normalization Parser

ARM template for ASIM NetworkSession schema parser for CrowdStrike Falcon Data Replicator.

Normalizes CrowdStrike_Network_Events_CL connection, accept, listen, close, raw-bind, and firewall-match events to the ASIM Network Session schema. Firewall-rule configuration and local-address removal events are excluded. event_simpleName is the authoritative event type and is expected to be populated.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM NetworkSession normalization schema reference](https://aka.ms/ASimNetworkSessionDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/CHANGELOG/ASimNetworkSessionCrowdStrikeFalconDataReplicator.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimNetworkSession%2FARM%2FASimNetworkSessionCrowdStrikeFalconDataReplicator%2FASimNetworkSessionCrowdStrikeFalconDataReplicator.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimNetworkSession%2FARM%2FASimNetworkSessionCrowdStrikeFalconDataReplicator%2FASimNetworkSessionCrowdStrikeFalconDataReplicator.json)
