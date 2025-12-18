# [Deprecated] Blackberry CylancePROTECT

| | |
|----------|-------|
| **Connector ID** | `BlackberryCylancePROTECT` |
| **Publisher** | Blackberry |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Blackberry CylancePROTECT](../solutions/blackberry-cylanceprotect.md) |
| **Connector Definition Files** | [template_BlackberryCylancePROTECT.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Blackberry%20CylancePROTECT/Data%20Connectors/template_BlackberryCylancePROTECT.JSON) |

The [Blackberry CylancePROTECT](https://www.blackberry.com/us/en/products/blackberry-protect) connector allows you to easily connect your CylancePROTECT logs with Microsoft Sentinel. This gives you more insight into your organization's network and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission.

**Custom Permissions:**
- **CylancePROTECT**: must be configured to export logs via Syslog.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias CyclanePROTECT and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Blackberry%20CylancePROTECT/Parsers/CylancePROTECT.txt), on the second line of the query, enter the hostname(s) of your CyclanePROTECT device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

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

1.  Select the link below to open your workspace **agents configuration**, and select the **Syslog** tab.
2.  Select **Add facility** and choose from the drop-down list of facilities. Repeat for all the facilities you want to add.
3.  Mark the check boxes for the desired severities for each facility.
4.  Click **Apply**.
- **Open Syslog settings**

**3. Configure and connect the CylancePROTECT**

[Follow these instructions](https://docs.blackberry.com/content/dam/docs-blackberry-com/release-pdfs/en/cylance-products/syslog-guides/Cylance%20Syslog%20Guide%20v2.0%20rev12.pdf) to configure the CylancePROTECT to forward syslog. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

[← Back to Connectors Index](../connectors-index.md)
