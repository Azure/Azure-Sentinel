# Proofpoint On Demand Email Security ASIM EmailEvent Normalization Parser

ARM template for ASIM EmailEvent schema parser for Proofpoint On Demand Email Security.

Filters and normalizes message inspection records from ProofpointPODMessage_CL
to ASIM EmailEvent without expanding recipients or MIME parts. Filter disposition
is not delivery confirmation. IPv4 prefix filtering uses has_any_ipv4_prefix.
Delivery location is unavailable; a nonempty delivery-location filter returns no rows.
Live source sampling and schema/data/filter validation are deferred by user direction.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM EmailEvent normalization schema reference](https://aka.ms/ASimEmailEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimEmailEvent/CHANGELOG/vimEmailEventProofpointPODMessage.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FvimEmailEventProofpointPODMessage%2FvimEmailEventProofpointPODMessage.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FvimEmailEventProofpointPODMessage%2FvimEmailEventProofpointPODMessage.json)
