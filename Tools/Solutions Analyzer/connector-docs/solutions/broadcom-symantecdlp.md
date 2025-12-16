# Broadcom SymantecDLP

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Broadcom Symantec DLP via Legacy Agent](../connectors/broadcomsymantecdlp.md)

**Publisher:** Broadcom

### [[Deprecated] Broadcom Symantec DLP via AMA](../connectors/broadcomsymantecdlpama.md)

**Publisher:** Broadcom

The [Broadcom Symantec Data Loss Prevention (DLP)](https://www.broadcom.com/products/cyber-security/information-protection/data-loss-prevention) connector allows you to easily connect your Symantec DLP with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization’s information, where it travels, and improves your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias SymantecDLP and load the function code or click [here](https://aka.ms/sentinel-symantecdlp-parser). The function usually takes 10-15 minutes to activate after solution installation/update.
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Forward Symantec DLP logs to a Syslog agent**

  Configure Symantec DLP to forward Syslog messages in CEF format to your Microsoft Sentinel workspace via the Syslog agent.
1. [Follow these instructions](https://knowledge.broadcom.com/external/article/159509/generating-syslog-messages-from-data-los.html) to configure the Symantec DLP to forward syslog
2. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

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
| **Connector Definition Files** | [template_SymantecDLPAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP/Data%20Connectors/template_SymantecDLPAMA.json) |

[→ View full connector details](../connectors/broadcomsymantecdlpama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Broadcom Symantec DLP via AMA](../connectors/broadcomsymantecdlpama.md), [[Deprecated] Broadcom Symantec DLP via Legacy Agent](../connectors/broadcomsymantecdlp.md) |

[← Back to Solutions Index](../solutions-index.md)
