This template deploys all ASIM FileEvent parsers. The template is part of the Advanced SIEM Information Model (ASIM).

The Advanced SIEM Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced SIEM Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)
- [Microsoft Sentinel FileEvent normalization schema reference](https://aka.ms/AzSentinelFileEventDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelFileEventARM)

<br>

The template deploys parsers for the following products:
* vimFileEventEmpty - An empty FileEvent table
* vimFileEventGeneric - Source agnostic parser
* vimFileEventMicrosoftDefender - Microsoft Defender 
* vimFileEventMicrosoftFileStorage - Microsoft Azure File Storage
* vimFileEventMicrosoftSharePoint - Microsoft SharePoint
* vimFileEventMicrosoftSysmonFileCreated - Sysmon File Created event (EventId 11)
* vimFileEventMicrosoftSysmonFileDeleted - Sysmon File Deleted events (EventId 23, 26) 

<br>

