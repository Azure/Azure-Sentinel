# Proofpoint TAP ASIM EmailEvent Normalization Parser

ARM template for ASIM EmailEvent schema parser for Proofpoint TAP.

Filters and normalizes Proofpoint TAP messages-blocked events from ProofPointTAPMessagesBlockedV2_CL to ASIM EmailEvent.
Supports event-time, IPv4-prefix, sender, recipient, subject, result, direction, delivery-location, disable, and packing parameters.
Result filters match Failure; delivery-location filters match Quarantine. The original quarantine folder and rule are retained.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM EmailEvent normalization schema reference](https://aka.ms/ASimEmailEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimEmailEvent/CHANGELOG/vimEmailEventProofpointTAPBlocked.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FvimEmailEventProofpointTAPBlocked%2FvimEmailEventProofpointTAPBlocked.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FvimEmailEventProofpointTAPBlocked%2FvimEmailEventProofpointTAPBlocked.json)
