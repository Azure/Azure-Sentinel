# CrowdStrike Falcon Data Replicator ASIM NetworkSession Normalization Parser

ARM template for ASIM NetworkSession schema parser for CrowdStrike Falcon Data Replicator.

Normalizes CrowdStrike_Network_Events_CL connection, accept, listen, close, raw-bind, and firewall-match events to the ASIM Network Session schema. Firewall-rule configuration and local-address removal events are excluded. event_simpleName is the authoritative event type and is expected to be populated.
Maps IPv4 and IPv6 endpoints, ports, local user and process identifiers, interfaces, and ICMP fields even when those source columns are empty in initial samples. Unknown direction codes leave source and destination roles unassigned. Undocumented numeric firewall actions remain raw rather than being translated. EventResult defaults to Success as prescribed by the schema unless a recognized denial or nonzero TCP error is present; this is not proof of a completed connection.
Source-only metadata and original action codes are retained in AdditionalFields only when pack is true. No hostname, domain, byte count, session duration, or TCP-flag value is inferred from unrelated source fields.
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
