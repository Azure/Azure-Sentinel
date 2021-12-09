# Advanced SIEM Information Model (ASIM) Network Session parsers 

This template deploys all ASIM Network parsers. The template is part of the Advanced SIEM Information Model (ASIM).

The Advanced SIEM Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced SIEM Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Microsoft Sentinel Network Session normalization schema reference](https://aka.ms/ASimNetworkSessionDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimNetworkSessionARM)

<br>

This page refers to Version 0.2 of the ASIM NetworkSession schema. If you are looking for Version 0.1 ASIM Network Session parsers refer to the [ASimNetworkSessionV1](https://github.com/Azure/Azure-Sentinel/tree/master/Parsers/ASimNetworkSession/ASimNetworkSessionV1) folder.

## Parsers

The template deploys the following parsers:

- Source Agnostic parsers:
  - **ASimNetworkSession** - Use this parser when you want to query interactively your Network Session logs.
  - **imNetworkSession** - Use this parser, which supports filtering parameters, when using Network Session logs in your content such as detections, hunting queries or workbooks. You can also use it interactively if you want to optimize your queries.
  - **vimNetworkSessionEmpty** - Empty ASIM NetworkSession table.

- Source specific parsers:
  - **Microsoft 365 Defender for Endpoints** - vimNetworkSessionMicrosoft365Defender, ASimNetworkSessionMicrosoft365Defender
  - **Microsoft Defender for IoT - Endpoint (MD4IoT)** - vimNetworkSessionMD4IoT, ASimNetworkSessionMD4IoT
  - **Microsoft Sysmon for Linux** - vimNetworkSessionSysmonLinux, ASimNetworkSessionSysmonLinux
  - **Windows Events Firewall** - Windows firewall activity as collected using Windows Events 515x, collected using either the Log Analytics Agent or the Azure Monitor Agent into either the Event or the WindowsEvent table, vimNetworkSessionMicrosoftWindowsEventFirewall, ASimNetworkSessionMicrosoftWindowsEventFirewall
