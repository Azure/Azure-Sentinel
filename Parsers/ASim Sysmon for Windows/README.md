# ASIM parsers for Sysmon for Windows

This template deploys all the [Sysmon for Windows](https://docs.microsoft.com/sysinternals/downloads/sysmon) Microsoft Sentinel ASIM parsers. The template is part of the [Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM). The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

When deploying the parsers, you:

- Make sure that telemetry from Sysmon is analyzed using the built-in Microsoft Sentinel Analytics. You also enable analysts easier access to the telemetry using a known, standard, schema.
- That events collected to the Event table and to the WindowsEvent tables (used by WEF) are both both available to analysts and in the same format.

**Note: to get the best value from ASIM and make sure that Sysmon telemetry is included in Microsoft Sentinel Analytics, deploy the [full ASIM parser suite](https://aka.ms/DeployASIM).**

<br>

[![Deploy to Microsoft Sentinel](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimSysmonARM)

<br>

The template deploys the following:

- ASIM Sysmon File Activity (11, 23 and 26) parsers - vimFileEventMicrosoftSysmon
- ASIM Sysmon Process Events (1 and 5) parsers - vimProcessCreateMicrosoftSysmon, vimProcessTerminateMicrosoftSysmon
- ASIM Sysmon Registry Events (12,13 and 14) parser - vimRegistryEventMicrosoftSysmon
- ASIM Sysmon DNS event (22) parsers - ASimDnsMicrosoftSysmon (regular), vimDnsMicrosoftSysmon (parametrized)

<br>
