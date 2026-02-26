# ASIM parsers for Sysmon for Linux

This template deploys all the development versions of [Sysmon for Linux](https://github.com/microsoft/SysmonForLinux) Microsoft Sentinel ASIM parsers. The template is part of the [Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM). The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

Note that production versions of Sysmon for Linux ASIM parsers are built into Sentinel and are available in every Sentinel workspace. Use this deployment to deploy a development version. For more information regarding workspace deployed parsers refer to refer to the [ASIM parser documentation](https://learn.microsoft.com/en-us/azure/sentinel/normalization-parsers-overview#built-in-asim-parsers-and-workspace-deployed-parsers)

To use the built-in ASIM Sysmon for Linux parsers just use the ASIM views that include Sysmon for Linux parsers.

- _Im_FileEvent
- _Im_NetworkSession
- _Im_ProcessCreate
- _Im_ProcessEvent
- _Im_ProcessTerminate

When using those ASIM views, Sysmon for Linux events are automatically included.

<br>

[![Deploy to Microsoft Sentinel](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimSysmonForLinuxARM)

