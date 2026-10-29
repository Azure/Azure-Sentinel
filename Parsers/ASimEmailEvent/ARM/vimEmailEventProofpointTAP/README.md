# Proofpoint TAP ASIM EmailEvent Normalization Parser

ARM template for ASIM EmailEvent schema parser for Proofpoint TAP.

Filters and normalizes Proofpoint TAP messages-delivered events from ProofPointTAPMessagesDeliveredV2_CL to ASIM EmailEvent.
Supports event-time, IPv4-prefix, sender, recipient, subject, direction, result, disable, and optional packing parameters.
Recipient filtering includes envelope, To, and CC recipients. Direction is Unknown and destination folder is unavailable;
a nonempty delivery-location filter returns no events. Missing messageTime falls back to TimeGenerated.
Preserves the parameterless parser mappings, including currently empty columns, without expanding source records.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM EmailEvent normalization schema reference](https://aka.ms/ASimEmailEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimEmailEvent/CHANGELOG/vimEmailEventProofpointTAP.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FvimEmailEventProofpointTAP%2FvimEmailEventProofpointTAP.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FvimEmailEventProofpointTAP%2FvimEmailEventProofpointTAP.json)
