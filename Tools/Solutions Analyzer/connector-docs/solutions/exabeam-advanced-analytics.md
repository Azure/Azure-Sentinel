# Exabeam Advanced Analytics

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Exabeam%20Advanced%20Analytics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Exabeam%20Advanced%20Analytics) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Exabeam Advanced Analytics](../connectors/exabeam.md)

**Publisher:** Exabeam

The [Exabeam Advanced Analytics](https://www.exabeam.com/ueba/advanced-analytics-and-mitre-detect-and-stop-threats/) data connector provides the capability to ingest Exabeam Advanced Analytics events into Microsoft Sentinel. Refer to [Exabeam Advanced Analytics documentation](https://docs.exabeam.com/) for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias Exabeam Advanced Analytics and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Exabeam%20Advanced%20Analytics/Parsers/ExabeamEvent.txt), on the second line of the query, enter the hostname(s) of your Exabeam Advanced Analytics device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

>**NOTE:** This data connector has been developed using Exabeam Advanced Analytics i54 (Syslog)

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the server where the Exabeam Advanced Analytic logs are generated or forwarded.

> Logs from Exabeam Advanced Analytic deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

Configure the custom log directory to be collected
- **Open custom logs settings**

**3. Configure Exabeam event forwarding to Syslog**

[Follow these instructions](https://docs.exabeam.com/en/advanced-analytics/i56/advanced-analytics-administration-guide/125351-advanced-analytics.html#UUID-7ce5ff9d-56aa-93f0-65de-c5255b682a08) to send Exabeam Advanced Analytics activity log data via syslog.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Exabeam_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Exabeam%20Advanced%20Analytics/Data%20Connectors/Connector_Exabeam_Syslog.json) |

[→ View full connector details](../connectors/exabeam.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Exabeam Advanced Analytics](../connectors/exabeam.md) |

[← Back to Solutions Index](../solutions-index.md)
