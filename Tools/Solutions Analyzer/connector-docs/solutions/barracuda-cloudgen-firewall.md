# Barracuda CloudGen Firewall

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2021-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Barracuda CloudGen Firewall](../connectors/barracudacloudfirewall.md)

**Publisher:** Barracuda

The Barracuda CloudGen Firewall (CGFW) connector allows you to easily connect your Barracuda CGFW logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Custom Permissions:**
- **Barracuda CloudGen Firewall**: must be configured to export logs via Syslog

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias CGFWFirewallActivity and load the function code or click [here](https://aka.ms/sentinel-barracudacloudfirewall-parser). The function usually takes 10-15 minutes to activate after solution installation/update.

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

**2. Configure and connect the Barracuda CloudGen Firewall**

[Follow instructions](https://aka.ms/sentinel-barracudacloudfirewall-connector) to configure syslog streaming. Use the IP address or hostname for the Linux machine with the Microsoft Sentinel agent installed for the Destination IP address.
- **Open Syslog settings**

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [template_BarracudaCloudFirewall.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall/Data%20Connectors/template_BarracudaCloudFirewall.json) |

[→ View full connector details](../connectors/barracudacloudfirewall.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Barracuda CloudGen Firewall](../connectors/barracudacloudfirewall.md) |

[← Back to Solutions Index](../solutions-index.md)
