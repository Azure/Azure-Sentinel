# Microsoft Windows Events Sysmon ASIM Dns Normalization Parser

This template deploys the ASIM DNS schema parser for Microsoft Windows Events Sysmon.  The parser is a part of the Advanced Security Information Model.

Normalize Sysmon for Windows DNS events (event number 22) collected using the Log Analytics agent to the ASIM DNS activity normalized schema. The parser supports events collected to both the Event and WindowsEvent tables.

The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced SIEM Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM Dns normalization schema reference](https://aka.ms/ASimDnsDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimDns%2FARM%2FASimDnsMicrosoftSysmon%2FASimDnsMicrosoftSysmon.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimDns%2FARM%2FASimDnsMicrosoftSysmon%2FASimDnsMicrosoftSysmon.json)
