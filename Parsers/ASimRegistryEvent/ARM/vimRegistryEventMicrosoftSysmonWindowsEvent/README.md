# Microsoft Sysmon ASIM RegistryEvent Normalization Parser

ARM template for ASIM RegistryEvent schema parser for Microsoft Sysmon.

This ASIM parser supports normalizing Microsoft Sysmon events (event number 12, 13, 14) logs ingested in 'WindowsEvent' table to the ASIM Registry Event normalized schema.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM RegistryEvent normalization schema reference](https://aka.ms/ASimRegistryEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimRegistryEvent/CHANGELOG/vimRegistryEventMicrosoftSysmonWindowsEvent.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimRegistryEvent%2FARM%2FvimRegistryEventMicrosoftSysmonWindowsEvent%2FvimRegistryEventMicrosoftSysmonWindowsEvent.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimRegistryEvent%2FARM%2FvimRegistryEventMicrosoftSysmonWindowsEvent%2FvimRegistryEventMicrosoftSysmonWindowsEvent.json)
