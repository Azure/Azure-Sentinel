# Advanced SIEM Information Model (ASIM) Network Session, Web Session and Network Notables parsers 

This template deploys all ASIM Network parsers. The template is part of the Advanced SIEM Information Model (ASIM).

The Advanced SIEM Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced SIEM Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)
- [Microsoft Sentinel Network Session normalization schema reference](https://aka.ms/AzSentinelNetworkSessionDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelNetworkSessionARM)

<br>

This page refers to Version 0.2 of the ASIM NetworkSession schema. If you are looking for Version 0.1 ASIM Network Session parsers refer to the [ASimNetworkSessionV1](https://github.com/Azure/Azure-Sentinel/tree/master/Parsers/ASimNetworkSession/ASimNetworkSessionV1) folder.

## Parsers

The template deploys the following parsers:

- Source Agnostic parsers:
  - **ASimWebSession** - Use this parser when you want to query interactively your Web Session logs.
  - **imWebSession** - Use this parser, which supports filtering parameters, when using Web Session logs in your content such as detections, hunting queries or workbooks. You can also use it interactively if you want to optimize your queries.
  - **vimSebSessionEmpty** - Empty ASIM WebSession table.
