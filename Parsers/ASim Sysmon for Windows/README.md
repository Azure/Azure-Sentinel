# ASIM parsers for Sysmon for Windows

This template deploys all the [Sysmon for Windows](https://docs.microsoft.com/sysinternals/downloads/sysmon) Azure Sentinel ASIM parsers. The template is part of the [Azure Sentinel Information Mode (ASIM)](https://aka.ms/AzSentinelNormalization). The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

When deploying the parsers, you:

- Make sure that telemetry from Sysmon is analyzed using the built-in Azure Sentinel Analytics. You also enable analysts easier access to the telemetry using a known, standard, schema.
- That events collected to the Event table and to the WindowsEvent tables (used by WEF) are both both available to analysts and in the same format.

**Note: to get the best value from ASIM and make sure that Sysmon telemetry is included in Azure Sentinel Analytics, deploy the [full ASIM parser suite](https://aka.ms/AzSentinelASim).**

<br>

[![Deploy to Azure Sentinel](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelSysmonARM)

<br>

The template deploys the following:

- ASIM Sysmon File Activity (11, 23 and 26) parsers - vimFileEventMicrosoftSysmonCreated, vimFileEventMicrosoftSysmonDeleted
- ASIM Sysmon Process Events (1 and 5) parsers - vimProcessCreateMicrosoftSysmon, vimProcessTerminateMicrosoftSysmon
- ASIM Sysmon Registry Events (12,13 and 14) parser - vimNetworkSessionLinuxSysmon
- ASIM Sysmon DNS event (22) parsers - ASimDnsMicrosoftSysmon (regular), vimDnsMicrosoftSysmon (parametrized)

<br>
