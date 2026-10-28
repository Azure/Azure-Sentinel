# Proofpoint Targeted Attack Protection ASIM EmailEvent Normalization Parser

ARM template for ASIM EmailEvent schema parser for Proofpoint Targeted Attack Protection.

Filters and normalizes ProofPointTAPClicksPermittedV2_CL URL Defense click records
as EmailInteraction activity without inferring email delivery or HTTP success.
Time filters use clickTime, falling back to TimeGenerated when clickTime is absent.
IPv4-prefix filters use the clicker's IP, and recipient filters use the source recipient.
Header From, subject, and delivery location are not supplied, so their filters can
match only when empty. Direction is Unknown and EventResult is NA.
Normalization and optional packing are identical to the parameterless parser.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM EmailEvent normalization schema reference](https://aka.ms/ASimEmailEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimEmailEvent/CHANGELOG/vimEmailEventProofpointTAPClicksPermitted.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FvimEmailEventProofpointTAPClicksPermitted%2FvimEmailEventProofpointTAPClicksPermitted.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FvimEmailEventProofpointTAPClicksPermitted%2FvimEmailEventProofpointTAPClicksPermitted.json)
