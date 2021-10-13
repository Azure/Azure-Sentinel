# ASIM parsers for Sysmon for Linux

This template deploys all the [upcoming Sysmon for Linux](https://twitter.com/markrussinovich/status/1283039153920368651?lang=en) Azure Sentinel ASIM parsers. The template is part of the [Azure Sentinel Information Mode (ASIM)](https://aka.ms/AzSentinelNormalization). The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

When deploying the parsers, you make sure that telemetry from Sysmon for Linux is analyzed using the built-in Azure Sentinel Analytics. You also enable analysts easier access to the telemetry using a known, standard, schema.

**Note: to get the best value from ASIM and make sure that Sysmon for Linux telemetry is included in Azure Sentinel Analytics, deploy the [full ASIM parser suite](https://aka.ms/AzSentinelASim).**

<br>

[![Deploy to Azure Sentinel](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelSysmonForLinuxARM)

<br>

The template deploys the following:

- ASIM Sysmon for Linux File Activity parsers - vimFileEventLinuxSysmonFileCreated, vimFileEventLinuxSysmonFileDeleted
- ASIM Sysmon for Linux Process Events parser - vimProcessCreateLinuxSysmon, vimProcessTerminateLinuxSysmon
- ASIM Sysmon for Linux Network Sessions parser - vimNetworkSessionLinuxSysmon

<br>
