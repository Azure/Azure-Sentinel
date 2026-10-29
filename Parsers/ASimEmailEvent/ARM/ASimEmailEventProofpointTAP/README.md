# Proofpoint TAP ASIM EmailEvent Normalization Parser

ARM template for ASIM EmailEvent schema parser for Proofpoint TAP.

Normalizes Proofpoint TAP messages-delivered events from ProofPointTAPMessagesDeliveredV2_CL to ASIM EmailEvent.
Includes mappings for currently empty source columns and preserves unmapped values in AdditionalFields when pack=true.
Preserves one normalized record per source row. Multiple threats and message parts remain available in AdditionalFields;
scalar threat fields and EmailFiles are populated only when the source provides a single corresponding item.
Message parts are not counted as attachments, and delivery does not imply a known destination folder or direction.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM EmailEvent normalization schema reference](https://aka.ms/ASimEmailEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimEmailEvent/CHANGELOG/ASimEmailEventProofpointTAP.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FASimEmailEventProofpointTAP%2FASimEmailEventProofpointTAP.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FASimEmailEventProofpointTAP%2FASimEmailEventProofpointTAP.json)
