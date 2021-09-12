# Azure Sentinel Information Model (ASIM) Network Session, Web Session and Network Notables parsers 

This template deploys all ASIM Network parsers. The template is part of the Azure Sentinel Information Mode (ASIM).

The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

For more information, see:

- [Normalization and the Azure Sentinel Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)
- [Azure Sentinel Network Session normalization schema reference](https://aka.ms/AzSentinelNetworkSessionDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelNetworkSessionARM)

<br>

## Parsers

The template deploys the following parsers:

- Source Agnostic parsers:
  - **imNetworkSession** - Network Session events from all normalized Network Session events sources.
  - **imWebSession** - Web Session events from all normalized Web Session event sources.
  - **imNetworkNotables** - Network and Web Sessions identified as notable by the reporting system.
  - **vimDnsEmpty** - Empty ASIM NetworkSession table.

- Source specific parsers:
  - **Microsoft 365 Defender for Endpoints** - vimNetworkSessionMicrosoft365Defender
  - **Azure Defender for IoT (AD4IoT)** - vimNetworkSessionAD4IoT
