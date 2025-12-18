# Akamai Security Events

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-03-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Akamai Security Events via Legacy Agent](../connectors/akamaisecurityevents.md)

**Publisher:** Akamai

### [[Deprecated] Akamai Security Events via AMA](../connectors/akamaisecurityeventsama.md)

**Publisher:** Akamai

Akamai Solution for Microsoft Sentinel provides the capability to ingest [Akamai Security Events](https://www.akamai.com/us/en/products/security/) into Microsoft Sentinel. Refer to [Akamai SIEM Integration documentation](https://developer.akamai.com/tools/integrations/siem) for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias Akamai Security Events and load the function code or click [here](https://aka.ms/sentinel-akamaisecurityevents-parser), on the second line of the query, enter the hostname(s) of your Akamai Security Events device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Forward Common Event Format (CEF) logs to Syslog agent**

  [Follow these steps](https://developer.akamai.com/tools/integrations/siem) to configure Akamai CEF connector to send Syslog messages in CEF format to the proxy machine. Make sure you to send the logs to port 514 TCP on the machine's IP address.

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
| **Connector Definition Files** | [template_AkamaiSecurityEventsAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events/Data%20Connectors/template_AkamaiSecurityEventsAMA.json) |

[→ View full connector details](../connectors/akamaisecurityeventsama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Akamai Security Events via AMA](../connectors/akamaisecurityeventsama.md), [[Deprecated] Akamai Security Events via Legacy Agent](../connectors/akamaisecurityevents.md) |

[← Back to Solutions Index](../solutions-index.md)
