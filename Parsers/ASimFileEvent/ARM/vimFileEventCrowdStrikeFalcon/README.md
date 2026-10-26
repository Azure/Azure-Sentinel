# CrowdStrike Falcon ASIM FileEvent Normalization Parser

ARM template for ASIM FileEvent schema parser for CrowdStrike Falcon.

Normalizes CrowdStrike Falcon Data Replicator file operations from CrowdStrike_File_Events_CL to ASIM FileEvent 1.0.0.
Filters by TimeGenerated, normalized event type, actor username, target and source file paths, and SHA256 hash.
The source provides neither an initiating source IP nor a device hostname; nonempty filters for these unavailable fields return no rows. The agent public IP aip maps to DvcIpAddr, not SrcIpAddr.
Uses populated event_simpleName without a fallback to name. FileDetectInfo, RansomwareFileAccessPattern, and unrecognized event names are excluded because they do not identify a supported file operation.
EventResult is NA because the connector definition does not document Status semantics. Unmapped vendor fields are retained only when pack=true.
This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM FileEvent normalization schema reference](https://aka.ms/ASimFileEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimFileEvent/CHANGELOG/vimFileEventCrowdStrikeFalcon.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimFileEvent%2FARM%2FvimFileEventCrowdStrikeFalcon%2FvimFileEventCrowdStrikeFalcon.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimFileEvent%2FARM%2FvimFileEventCrowdStrikeFalcon%2FvimFileEventCrowdStrikeFalcon.json)
