# [Deprecated] OpenVPN Server

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `OpenVPN` |
| **Publisher** | OpenVPN |
| **Used in Solutions** | [OpenVPN](../solutions/openvpn.md) |
| **Collection Method** | MMA |
| **Connector Definition Files** | [OpenVPN_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenVPN/Data%20Connectors/OpenVPN_Syslog.json) |

The [OpenVPN](https://github.com/OpenVPN) data connector provides the capability to ingest OpenVPN Server logs into Microsoft Sentinel.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`Syslog`](../tables/syslog.md) | ✓ | ✓ |

> 💡 **Tip:** Tables with Ingestion API support allow data ingestion via the [Azure Monitor Data Collector API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview), which also enables custom transformations during ingestion.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**OpenVpnEvent**](https://aka.ms/sentinel-openvpn-parser) which is deployed with the Microsoft Sentinel Solution.

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Server where the OpenVPN are forwarded.

> Logs from OpenVPN Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

1.  Under workspace advanced settings **Configuration**, select **Data** and then **Syslog**.
2.  Select **Apply below configuration to my machines** and select the facilities and severities.
3.  Click **Save**.
- **Open Syslog settings**

**3. Check your OpenVPN logs.**

OpenVPN server logs are written into common syslog file (depending on the Linux distribution used: e.g. /var/log/messages)

[← Back to Connectors Index](../connectors-index.md)
