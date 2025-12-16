# Pulse Connect Secure

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Pulse Connect Secure](../connectors/pulseconnectsecure.md)

**Publisher:** Pulse Secure

The [Pulse Connect Secure](https://www.pulsesecure.net/products/pulse-connect-secure/) connector allows you to easily connect your Pulse Connect Secure logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigations. Integrating Pulse Connect Secure with Microsoft Sentinel provides more insight into your organization's network and improves your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Custom Permissions:**
- **Pulse Connect Secure**: must be configured to export logs via Syslog

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias Pulse Connect Secure and load the function code or click [here](https://aka.ms/sentinel-PulseConnectSecure-parser), on the second line of the query, enter the hostname(s) of your Pulse Connect Secure device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

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

**3. Configure and connect the Pulse Connect Secure**

[Follow the instructions](https://help.ivanti.com/ps/help/en_US/PPS/9.1R13/ag/configuring_an_external_syslog_server.htm) to enable syslog streaming of Pulse Connect Secure logs. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_PulseConnectSecure.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure/Data%20Connectors/Connector_Syslog_PulseConnectSecure.json) |

[→ View full connector details](../connectors/pulseconnectsecure.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Pulse Connect Secure](../connectors/pulseconnectsecure.md) |

[← Back to Solutions Index](../solutions-index.md)
