# Microsoft Sysmon For Linux

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Sysmon%20For%20Linux](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Sysmon%20For%20Linux) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Microsoft Sysmon For Linux](../connectors/microsoftsysmonforlinux.md)

**Publisher:** Microsoft

[Sysmon for Linux](https://github.com/Sysinternals/SysmonForLinux) provides detailed information about process creations, network connections and other system events.

[Sysmon for linux link:]. The Sysmon for Linux connector uses [Syslog](https://aka.ms/sysLogInfo) as its data ingestion method. This solution depends on ASIM to work as expected. [Deploy ASIM](https://aka.ms/DeployASIM) to get the full value from the solution.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| | `vimProcessCreateLinuxSysmon` |
| **Connector Definition Files** | [SysmonForLinux.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Sysmon%20For%20Linux/Data%20Connectors/SysmonForLinux.json) |

[→ View full connector details](../connectors/microsoftsysmonforlinux.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Microsoft Sysmon For Linux](../connectors/microsoftsysmonforlinux.md) |
| `vimProcessCreateLinuxSysmon` | [[Deprecated] Microsoft Sysmon For Linux](../connectors/microsoftsysmonforlinux.md) |

[← Back to Solutions Index](../solutions-index.md)
