# Symantec Endpoint Protection

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-07-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20Endpoint%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20Endpoint%20Protection) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Symantec Endpoint Protection](../connectors/symantecendpointprotection.md)

**Publisher:** Broadcom

The [Broadcom Symantec Endpoint Protection (SEP)](https://www.broadcom.com/products/cyber-security/endpoint/end-user/enterprise) connector allows you to easily connect your SEP logs with Microsoft Sentinel. This gives you more insight into your organization's network and improves your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Custom Permissions:**
- **Symantec Endpoint Protection (SEP)**: must be configured to export logs via Syslog

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias Symantec Endpoint Protection and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20Endpoint%20Protection/Parsers/SymantecEndpointProtection.yaml), on the second line of the query, enter the hostname(s) of your SymantecEndpointProtection device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

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

**3. Configure and connect the Symantec Endpoint Protection**

[Follow these instructions](https://techdocs.broadcom.com/us/en/symantec-security-software/endpoint-security-and-management/endpoint-protection/all/Monitoring-Reporting-and-Enforcing-Compliance/viewing-logs-v7522439-d37e464/exporting-data-to-a-syslog-server-v8442743-d15e1107.html) to configure the Symantec Endpoint Protection to forward syslog. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_SymantecEndpointProtection.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20Endpoint%20Protection/Data%20Connectors/Connector_Syslog_SymantecEndpointProtection.json) |

[→ View full connector details](../connectors/symantecendpointprotection.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Symantec Endpoint Protection](../connectors/symantecendpointprotection.md) |

[← Back to Solutions Index](../solutions-index.md)
