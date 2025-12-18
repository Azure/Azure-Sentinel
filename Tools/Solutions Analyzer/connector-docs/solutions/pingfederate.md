# PingFederate

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] PingFederate via Legacy Agent](../connectors/pingfederate.md)

**Publisher:** Ping Identity

### [[Deprecated] PingFederate via AMA](../connectors/pingfederateama.md)

**Publisher:** Ping Identity

The [PingFederate](https://www.pingidentity.com/en/software/pingfederate.html) data connector provides the capability to ingest [PingFederate events](https://docs.pingidentity.com/bundle/pingfederate-102/page/lly1564002980532.html) into Microsoft Sentinel. Refer to [PingFederate documentation](https://docs.pingidentity.com/bundle/pingfederate-102/page/tle1564002955874.html) for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**PingFederateEvent**](https://aka.ms/sentinel-PingFederate-parser) which is deployed with the Microsoft Sentinel Solution.
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Forward Common Event Format (CEF) logs to Syslog agent**

  [Follow these steps](https://docs.pingidentity.com/bundle/pingfederate-102/page/gsn1564002980953.html) to configure PingFederate sending audit log via syslog in CEF format.

  **Step C. Validate connection**

  Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

 1. Make sure that you have Python on your machine using the following command: python -version

2. You must have elevated permissions (sudo) on your machine
  - **Run the following command to validate your connectivity:**: `sudo wget -O Sentinel_AMA_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/Syslog/Sentinel_AMA_troubleshoot.py&&sudo python Sentinel_AMA_troubleshoot.py --cef`

**2. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_PingFederateAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Data%20Connectors/template_PingFederateAMA.json) |

[→ View full connector details](../connectors/pingfederateama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] PingFederate via AMA](../connectors/pingfederateama.md), [[Deprecated] PingFederate via Legacy Agent](../connectors/pingfederate.md) |

[← Back to Solutions Index](../solutions-index.md)
