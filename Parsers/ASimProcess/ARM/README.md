# Azure Sentinel Information Model (ASIM) Process parsers 

This template deploys all ASIM Process parsers. The template is part of the Azure Sentinel Information Mode (ASIM).

The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

For more information, see:

- [Normalization and the Azure Sentinel Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)
- [Azure Sentinel process events normalization schema reference](https://aka.ms/AzSentinelProcessEventDoc)



<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelProcessEventARM)

<br>

This template deploys the following:
* vimProcessEmpty - Empty ASim Process table
* imProcess - Process Events from all normalized process events sources
* imProcessCreate - Process creation Events from all normalized process events sources
* imProcessTerminate - Process termination Events from all normalized process events sources
* vimProcessEventsMicrosoft365D - Process events from Microsoft 365 Defender for Endpoints
* vimProcessCreateMicrosoftSysmon - Process Creation Events from Sysmon
* vimProcessTermianteMicrosoftSysmon - Process Termination Events from Sysmon
* vimProcessCreateMicrosoftSecurityEvents - Process Creation Events from Security Events
* vimProcessTerminateMicrosoftSecurityEvents - Process Terination Events from Security Events

<br>







