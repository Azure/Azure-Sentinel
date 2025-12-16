# Watchguard Firebox

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | WatchGuard |
| **Support Tier** | Partner |
| **Support Link** | [https://www.watchguard.com/wgrd-support/contact-support](https://www.watchguard.com/wgrd-support/contact-support) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Watchguard%20Firebox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Watchguard%20Firebox) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] WatchGuard Firebox](../connectors/watchguardfirebox.md)

**Publisher:** WatchGuard Technologies

WatchGuard Firebox (https://www.watchguard.com/wgrd-products/firewall-appliances and https://www.watchguard.com/wgrd-products/cloud-and-virtual-firewalls) is security products/firewall-appliances. Watchguard Firebox will send syslog to Watchguard Firebox collector agent.The agent then sends the message to the workspace.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias WatchGuardFirebox and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Watchguard%20Firebox/Parsers/WatchGuardFirebox.txt) on the second line of the query, enter the hostname(s) of your WatchGuard Firebox device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

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
| **Connector Definition Files** | [Connector_syslog_WatchGuardFirebox.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Watchguard%20Firebox/Data%20Connectors/Connector_syslog_WatchGuardFirebox.json) |

[→ View full connector details](../connectors/watchguardfirebox.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] WatchGuard Firebox](../connectors/watchguardfirebox.md) |

[← Back to Solutions Index](../solutions-index.md)
