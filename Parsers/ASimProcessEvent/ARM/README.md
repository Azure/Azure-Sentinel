# Azure Sentinel Information Model (ASIM) ProcessEvent parsers 

This template deploys all ASIM ProcessEvent parsers. The template is part of the Azure Sentinel Information Mode (ASIM).

The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

For more information, see:

- [Normalization and the Azure Sentinel Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)
- [Azure Sentinel ProcessEvent normalization schema reference](https://aka.ms/AzSentinelProcessEventDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelProcessEventARM)

<br>

The template deploys the following:
* Source Agnostic parsers:
  * imProcess - Process events from all normalized process events sources
  * imProcessCreate - Process creation events from all normalized process events sources
  * imProcessTerminate - Process termination events from all normalized process events sources
  * vimProcessEmpty - Empty ASim Process table
* Source specific parsers:
  * **Microsoft 365 Defender for Endpoints** - vimProcessEventsMicrosoft365D
  * **Sysmon for Windows** - vimProcessCreateMicrosoftSysmon, vimProcessTerminateMicrosoftSysmon 
  * **Sysmon for Linux** - vimProcessCreateLinuxSysmon
  * **Windows Security Events**, collecting using the Log Analytics Agent or Azure Monitor Agent - vimProcessCreateMicrosoftSecurityEvents, vimProcessTerminateMicrosoftSecurityEvents
  * **Windows Events**, collecting using the Log Analytics Agent or Azure Monitor Agent - vimProcessCreationMicrosoftWindowsEvents, vimProcessTerminationMicrosoftWindowsEvents
  * **AzudeDefender for IoT (AD4IoT)** - vimProcessEventAD4IoT 

<br>

