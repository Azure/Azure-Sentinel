# Sophos XG Firewall

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Sophos XG Firewall](../connectors/sophosxgfirewall.md)

**Publisher:** Sophos

The [Sophos XG Firewall](https://www.sophos.com/products/next-gen-firewall.aspx) allows you to easily connect your Sophos XG Firewall logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigations. Integrating Sophos XG Firewall with Microsoft Sentinel provides more visibility into your organization's firewall traffic and will enhance security monitoring capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Custom Permissions:**
- **Sophos XG Firewall**: must be configured to export logs via Syslog

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias Sophos XG Firewall and load the function code or click [here](https://aka.ms/sentinel-SophosXG-parser), on the second line of the query, enter the hostname(s) of your Sophos XG Firewall device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

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

**3. Configure and connect the Sophos XG Firewall**

[Follow these instructions](https://doc.sophos.com/nsg/sophos-firewall/20.0/Help/en-us/webhelp/onlinehelp/AdministratorHelp/SystemServices/LogSettings/SyslogServerAdd/index.html) to enable syslog streaming. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_SophosXGFirewall.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall/Data%20Connectors/Connector_Syslog_SophosXGFirewall.json) |

[→ View full connector details](../connectors/sophosxgfirewall.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Sophos XG Firewall](../connectors/sophosxgfirewall.md) |

[← Back to Solutions Index](../solutions-index.md)
