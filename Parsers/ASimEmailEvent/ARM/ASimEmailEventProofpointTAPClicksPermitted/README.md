# Proofpoint Targeted Attack Protection ASIM EmailEvent Normalization Parser

ARM template for ASIM EmailEvent schema parser for Proofpoint Targeted Attack Protection.

Normalizes ProofPointTAPClicksPermittedV2_CL URL Defense click records as EmailEvent
interaction activity (EmailInteraction), preserving one event per source row. Permitting a click does
not establish email delivery or HTTP success, so EventResult and DvcAction are NA.
Event time uses clickTime, falling back to TimeGenerated when clickTime is absent.
EventOriginalUid preserves the optional source id when available and remains empty
when the id column is absent.
SrcIpAddr is the clicker's external IP; the email sender's IP is retained only
in AdditionalFields. The recipient maps to Dst, not to an inferred clicker identity
or message-header recipient. Header From, subject, and delivery location are unavailable.
EmailUrls contains the observed clicked URL, not a complete message URL inventory.
Message and campaign identifiers, sender IP, original threat status, and user agent
are retained when pack=true.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM EmailEvent normalization schema reference](https://aka.ms/ASimEmailEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimEmailEvent/CHANGELOG/ASimEmailEventProofpointTAPClicksPermitted.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FASimEmailEventProofpointTAPClicksPermitted%2FASimEmailEventProofpointTAPClicksPermitted.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FASimEmailEventProofpointTAPClicksPermitted%2FASimEmailEventProofpointTAPClicksPermitted.json)
