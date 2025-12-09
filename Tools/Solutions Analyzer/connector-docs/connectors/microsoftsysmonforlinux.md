# [Deprecated] Microsoft Sysmon For Linux

| | |
|----------|-------|
| **Connector ID** | `MicrosoftSysmonForLinux` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog), [`vimProcessCreateLinuxSysmon`](../tables-index.md#vimprocesscreatelinuxsysmon) |
| **Used in Solutions** | [Microsoft Sysmon For Linux](../solutions/microsoft-sysmon-for-linux.md) |
| **Connector Definition Files** | [SysmonForLinux.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Sysmon%20For%20Linux/Data%20Connectors/SysmonForLinux.json) |

[Sysmon for Linux](https://github.com/Sysinternals/SysmonForLinux) provides detailed information about process creations, network connections and other system events.

[Sysmon for linux link:]. The Sysmon for Linux connector uses [Syslog](https://aka.ms/sysLogInfo) as its data ingestion method. This solution depends on ASIM to work as expected. [Deploy ASIM](https://aka.ms/DeployASIM) to get the full value from the solution.

[← Back to Connectors Index](../connectors-index.md)
