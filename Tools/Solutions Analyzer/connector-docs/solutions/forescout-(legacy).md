# Forescout (Legacy)

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20%28Legacy%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20%28Legacy%29) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Forescout](../connectors/forescout.md)

**Publisher:** Forescout

The [Forescout](https://www.forescout.com/) data connector provides the capability to ingest [Forescout events](https://docs.forescout.com/bundle/syslog-3-6-1-h/page/syslog-3-6-1-h.How-to-Work-with-the-Syslog-Plugin.html) into Microsoft Sentinel. Refer to [Forescout documentation](https://docs.forescout.com/bundle/syslog-msg-3-6-tn/page/syslog-msg-3-6-tn.About-Syslog-Messages-in-Forescout.html) for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**ForescoutEvent**](https://aka.ms/sentinel-forescout-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:** This data connector has been developed using Forescout Syslog Plugin version: v3.6

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Server where the Forescout logs are forwarded.

> Logs from Forescout Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
**Choose where to install the Linux agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**Choose where to install the Windows agent:**

**Install agent on Azure Windows Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install/configure: InstallAgentOnVirtualMachine**

  **Install agent on a non-Azure Windows Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install/configure: InstallAgentOnNonAzure**

**2. Configure the logs to be collected**

Configure the facilities you want to collect and their severities.
 1. Under workspace advanced settings **Configuration**, select **Data** and then **Syslog**.
 2. Select **Apply below configuration to my machines** and select the facilities and severities.
 3.  Click **Save**.
- **Open Syslog settings**

**3. Configure Forescout event forwarding**

Follow the configuration steps below to get Forescout logs into Microsoft Sentinel.
1. [Select an Appliance to Configure.](https://docs.forescout.com/bundle/syslog-3-6-1-h/page/syslog-3-6-1-h.Select-an-Appliance-to-Configure.html)
2. [Follow these instructions](https://docs.forescout.com/bundle/syslog-3-6-1-h/page/syslog-3-6-1-h.Send-Events-To-Tab.html#pID0E0CE0HA) to forward alerts from the Forescout platform to a syslog server.
3. [Configure](https://docs.forescout.com/bundle/syslog-3-6-1-h/page/syslog-3-6-1-h.Syslog-Triggers.html) the settings in the Syslog Triggers tab.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Forescout_syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20%28Legacy%29/Data%20Connectors/Forescout_syslog.json) |

[→ View full connector details](../connectors/forescout.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [Forescout](../connectors/forescout.md) |

[← Back to Solutions Index](../solutions-index.md)
