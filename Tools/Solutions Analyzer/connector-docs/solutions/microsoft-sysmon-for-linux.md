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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>This data connector depends on ASIM parsers based on a Kusto Functions to work as expected. [Deploy the parsers](https://aka.ms/ASimSysmonForLinuxARM) 

 The following functions will be deployed:

 - vimFileEventLinuxSysmonFileCreated, vimFileEventLinuxSysmonFileDeleted

 - vimProcessCreateLinuxSysmon, vimProcessTerminateLinuxSysmon

 - vimNetworkSessionLinuxSysmon 

[Read more](https://aka.ms/AboutASIM)

**1. Install and onboard the agent for Linux**

Typically, you should install the agent on a different computer from the one on which the logs are generated.

>  Syslog logs are collected only from **Linux** agents.
**Choose where to install the agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**2. Configure the logs to be collected**

Configure the facilities you want to collect and their severities.

1.  Under workspace advanced settings **Configuration**, select **Data** and then **Syslog**.
2.  Select **Apply below configuration to my machines** and select the facilities and severities.
3.  Click **Save**.
- **Open Syslog settings**

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
