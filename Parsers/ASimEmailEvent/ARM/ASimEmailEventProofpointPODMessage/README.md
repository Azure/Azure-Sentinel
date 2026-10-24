# Proofpoint On Demand Email Security ASIM EmailEvent Normalization Parser

ARM template for ASIM EmailEvent schema parser for Proofpoint On Demand Email Security.

Normalizes message inspection records from the CCP connector's ProofpointPODMessage_CL
table to ASIM EmailEvent. Each source message remains one event, including messages
with multiple recipients or MIME parts. Filter disposition is not delivery confirmation.
DMARC quarantine/reject normalize to Fail and retain their policy; pass/none normalize
case-insensitively. DMARC temperror/permerror retain their original value but have no
normalized result because EmailEvent has no matching error enumeration.
Dispositions reject/discard map to Blocked, hold to Quarantined, redirect to Redirected,
and continue/accept/retry to NA without asserting successful delivery.
Live source sampling and schema/data validation are deferred by user direction.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM EmailEvent normalization schema reference](https://aka.ms/ASimEmailEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimEmailEvent/CHANGELOG/ASimEmailEventProofpointPODMessage.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FASimEmailEventProofpointPODMessage%2FASimEmailEventProofpointPODMessage.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FASimEmailEventProofpointPODMessage%2FASimEmailEventProofpointPODMessage.json)
