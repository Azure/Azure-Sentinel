# ASIM parsers for Sysmon for Windows

This template deploys all the development versions of [Sysmon](https://learn.microsoft.com/sysinternals/downloads/sysmon) Microsoft Sentinel ASIM parsers. The template is part of the [Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM). The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

Note that production versions of Sysmon ASIM parsers are built into Sentinel and are available in every Sentinel workspace. Use this deployment to deploy a development version. For more information regarding workspace deployed parsers refer to refer to the [ASIM parser documentation](https://learn.microsoft.com/en-us/azure/sentinel/normalization-parsers-overview#built-in-asim-parsers-and-workspace-deployed-parsers)

To use the built-in ASIM Sysmon parsers just use the ASIM views that include Sysmon parsers.

- _Im_Dns (includes Sysmon event 22)
- _Im_FileEvent (includes Sysmon events 11, 23 and 26)
- _Im_NetworkSession (includes Sysmon event 3)
- _Im_ProcessEvent (includes Sysmon events 1 and 5)
- _Im_ProcessCreate (includes Sysmon event 1)
- _Im_ProcessTerminate (includes Sysmon event 5)
- _Im_RegistryEvent (includes Sysmon events 12,13 and 14)

When using those ASIM views, Sysmon events are automatically included.

<br>

[![Deploy to Microsoft Sentinel](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimSysmonARM)

<br>
