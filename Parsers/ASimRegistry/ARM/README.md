# Azure Sentinel Information Model (ASIM) Registry parsers 

This template deploys all ASIM Registry parsers. The template is part of the Azure Sentinel Information Mode (ASIM).

The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

For more information, see:

- [Normalization and the Azure Sentinel Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)
- [Azure Sentinel Registry events normalization schema reference](https://aka.ms/AzSentinelRegistryEventDoc)



<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelRegistryEventARM)

<br>

This template deploys the following:
* vimRegistryEmpty - Empty ASim Registry table
* imRegistry - Registry Events from all normalized Registry events sources
* vimRegistryEventsMicrosoft365D - Registry events from Microsoft 365 Defender for Endpoints
* vimRegistryEventMicrosoftSysmon - Registry events from Sysmon (Events 12,13 and 14) collected using the Log Analytics Agent or the Azure Monitor Agent to the Event table.
* vimRegistryEventMicrosoftSecurityEvents - Registry Events from Windows Events (Event 4657) collected using the Log Analytics Agent or the Azure Monitor Agent to the SecuirtyEvent table.

<br>







