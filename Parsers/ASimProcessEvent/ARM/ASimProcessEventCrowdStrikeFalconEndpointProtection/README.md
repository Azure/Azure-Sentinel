# CrowdStrike Falcon Endpoint Protection ASIM ProcessEvent Normalization Parser

ARM template for ASIM ProcessEvent schema parser for CrowdStrike Falcon Endpoint Protection.

Normalizes CrowdStrike_Process_Events_CL process creation, synthetic process observations,
process termination, and termination requests to ASIM ProcessEvent 1.0.0.
Uses event_simpleName when present and recognized versioned name values otherwise.
Excludes unidentified events, file operations, module loads, and process injection.
Native OS process IDs are mapped only when attributable to the corresponding role.
Unavailable identities remain empty; Falcon correlation IDs are not relabeled as OS PIDs.
Termination requests have EventResult NA because successful termination is not established.
Set pack=true to preserve raw source fields in AdditionalFields, including fields without
standard ProcessEvent equivalents. Empty source values are omitted from the packed bag.
Vendor field documentation requires authentication; the public references cover the product
and process-event context, not a complete authoritative field dictionary.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM ProcessEvent normalization schema reference](https://aka.ms/ASimProcessEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/CHANGELOG/ASimProcessEventCrowdStrikeFalconEndpointProtection.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimProcessEvent%2FARM%2FASimProcessEventCrowdStrikeFalconEndpointProtection%2FASimProcessEventCrowdStrikeFalconEndpointProtection.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimProcessEvent%2FARM%2FASimProcessEventCrowdStrikeFalconEndpointProtection%2FASimProcessEventCrowdStrikeFalconEndpointProtection.json)
