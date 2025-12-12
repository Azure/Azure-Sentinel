# PaloAltoCDL

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via Legacy Agent](../connectors/paloaltocdl.md)

**Publisher:** Palo Alto Networks

### [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via AMA](../connectors/paloaltocdlama.md)

**Publisher:** Palo Alto Networks

The [Palo Alto Networks CDL](https://www.paloaltonetworks.com/cortex/cortex-data-lake) data connector provides the capability to ingest [CDL logs](https://docs.paloaltonetworks.com/strata-logging-service/log-reference/log-forwarding-schema-overview) into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**PaloAltoCDLEvent**](https://aka.ms/sentinel-paloaltocdl-parser) which is deployed with the Microsoft Sentinel Solution.
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Configure Cortex Data Lake to forward logs to a Syslog Server using CEF**

  [Follow the instructions](https://docs.paloaltonetworks.com/cortex/cortex-data-lake/cortex-data-lake-getting-started/get-started-with-log-forwarding-app/forward-logs-from-logging-service-to-syslog-server.html) to configure logs forwarding from Cortex Data Lake to a Syslog Server.

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
| **Connector Definition Files** | [template_PaloAlto_CDLAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Data%20Connectors/template_PaloAlto_CDLAMA.json) |

[→ View full connector details](../connectors/paloaltocdlama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via AMA](../connectors/paloaltocdlama.md), [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via Legacy Agent](../connectors/paloaltocdl.md) |

[← Back to Solutions Index](../solutions-index.md)
