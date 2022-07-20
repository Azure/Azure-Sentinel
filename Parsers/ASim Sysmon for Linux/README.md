# ASIM parsers for Sysmon for Linux

This template deploys all the [upcoming Sysmon for Linux](https://twitter.com/markrussinovich/status/1283039153920368651?lang=en) Microsoft Sentinel ASIM parsers. The template is part of the [Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM). The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

When deploying the parsers, you make sure that telemetry from Sysmon for Linux is analyzed using the built-in Microsoft Sentinel Analytics. You also enable analysts easier access to the telemetry using a known, standard, schema.

**Note: to get the best value from ASIM and make sure that Sysmon for Linux telemetry is included in Microsoft Sentinel Analytics, deploy the [full ASIM parser suite](https://aka.ms/DeployASIM).**

<br>

[![Deploy to Microsoft Sentinel](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimSysmonForLinuxARM)

<br>

The template deploys the following:

- ASIM Sysmon for Linux File Activity parsers - vimFileEventLinuxSysmonFileCreated, vimFileEventLinuxSysmonFileDeleted
- ASIM Sysmon for Linux Process Events parser - vimProcessCreateLinuxSysmon, vimProcessTerminateLinuxSysmon
- ASIM Sysmon for Linux Network Sessions parser - vimNetworkSessionLinuxSysmon

<br>
