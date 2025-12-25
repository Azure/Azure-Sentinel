# [Deprecated] Citrix WAF (Web App Firewall) via AMA

| | |
|----------|-------|
| **Connector ID** | `CitrixWAFAma` |
| **Publisher** | Citrix Systems Inc. |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Citrix Web App Firewall](../solutions/citrix-web-app-firewall.md) |
| **Connector Definition Files** | [template_Citrix_WAFAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Web%20App%20Firewall/Data%20Connectors/template_Citrix_WAFAMA.json) |

 Citrix WAF (Web App Firewall) is an industry leading enterprise-grade WAF solution. Citrix WAF mitigates threats against your public-facing assets, including websites, apps, and APIs. From layer 3 to layer 7, Citrix WAF includes protections such as IP reputation, bot mitigation, defense against the OWASP Top 10 application threats, built-in signatures to protect against application stack vulnerabilities, and more. 



Citrix WAF supports Common Event Format (CEF) which is an industry standard format on top of Syslog messages . By connecting Citrix WAF CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Microsoft Sentinel.

> Notice that the data from all regions will be stored in the selected workspace
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Forward Common Event Format (CEF) logs to Syslog agent**

  Configure Citrix WAF to send Syslog messages in CEF format to the proxy machine using the steps below. 

1. Follow [this guide](https://support.citrix.com/article/CTX234174) to configure WAF.

2. Follow [this guide](https://support.citrix.com/article/CTX136146) to configure CEF logs.

3. Follow [this guide](https://docs.citrix.com/en-us/citrix-adc/13/system/audit-logging/configuring-audit-logging.html) to forward the logs to proxy . Make sure you to send the logs to port 514 TCP on the Linux machine's IP address.

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

[← Back to Connectors Index](../connectors-index.md)
