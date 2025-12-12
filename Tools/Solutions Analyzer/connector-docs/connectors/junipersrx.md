# [Deprecated] Juniper SRX

| | |
|----------|-------|
| **Connector ID** | `JuniperSRX` |
| **Publisher** | Juniper |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Juniper SRX](../solutions/juniper-srx.md) |
| **Connector Definition Files** | [Connector_Syslog_JuniperSRX.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Juniper%20SRX/Data%20Connectors/Connector_Syslog_JuniperSRX.json) |

The [Juniper SRX](https://www.juniper.net/us/en/products-services/security/srx-series/) connector allows you to easily connect your Juniper SRX logs with Microsoft Sentinel. This gives you more insight into your organization's network and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Custom Permissions:**
- **Juniper SRX**: must be configured to export logs via Syslog

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias JuniperSRX and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Juniper%20SRX/Parsers/JuniperSRX.txt), on the second line of the query, enter the hostname(s) of your JuniperSRX device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

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

**3. Configure and connect the Juniper SRX**

1. Follow these instructions to configure the Juniper SRX to forward syslog: 
 - [Traffic Logs (Security Policy Logs)](https://kb.juniper.net/InfoCenter/index?page=content&id=KB16509&actp=METADATA) 
 - [System Logs](https://kb.juniper.net/InfoCenter/index?page=content&id=kb16502)
2. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

[← Back to Connectors Index](../connectors-index.md)
