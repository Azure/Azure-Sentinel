# [Deprecated] Infoblox NIOS

| | |
|----------|-------|
| **Connector ID** | `InfobloxNIOS` |
| **Publisher** | Infoblox |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Infoblox NIOS](../solutions/infoblox-nios.md) |
| **Connector Definition Files** | [Connector_Syslog_Infoblox.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Data%20Connectors/Connector_Syslog_Infoblox.json) |

The [Infoblox Network Identity Operating System (NIOS)](https://www.infoblox.com/glossary/network-identity-operating-system-nios/) connector allows you to easily connect your Infoblox NIOS logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Custom Permissions:**
- **Infoblox NIOS**: must be configured to export logs via Syslog

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias Infoblox and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parser/Infoblox.yaml), on the second line of the query, enter any unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

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
 1. Under workspace advanced settings **Configuration**, select **Data** and then **Syslog**.
 2. Select **Apply below configuration to my machines** and select the facilities and severities.
 3.  Click **Save**.
- **Open Syslog settings**

**3. Configure and connect the Infoblox NIOS**

[Follow these instructions](https://www.infoblox.com/wp-content/uploads/infoblox-deployment-guide-slog-and-snmp-configuration-for-nios.pdf) to enable syslog forwarding of Infoblox NIOS Logs. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

**4. Configure the Sentinel parser**

Update the watchlist 'Sources_by_Source' with the hostname(s) of your Infoblox device(s). Set SourceType to 'InfobloxNIOS' and Source to the value of 'Computer' seen in the logs seen in Syslog table.

[← Back to Connectors Index](../connectors-index.md)
