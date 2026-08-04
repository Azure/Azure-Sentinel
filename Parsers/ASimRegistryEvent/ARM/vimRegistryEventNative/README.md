# Native ASIM RegistryEvent Normalization Parser

ARM template for ASIM RegistryEvent schema parser for Native.

This ASIM parser supports normalizing the native Registry Event table (ASimRegistryEventLogs) to the ASIM Registry Event normalized schema. While the native table is ASIM compliant, the parser is needed to add capabilities, such as aliases, available only at query time.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM RegistryEvent normalization schema reference](https://aka.ms/ASimRegistryEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimRegistryEvent/CHANGELOG/vimRegistryEventNative.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimRegistryEvent%2FARM%2FvimRegistryEventNative%2FvimRegistryEventNative.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimRegistryEvent%2FARM%2FvimRegistryEventNative%2FvimRegistryEventNative.json)
