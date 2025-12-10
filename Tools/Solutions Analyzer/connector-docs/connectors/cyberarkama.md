# [Deprecated] CyberArk Privilege Access Manager (PAM) Events via AMA

| | |
|----------|-------|
| **Connector ID** | `CyberArkAma` |
| **Publisher** | Cyber-Ark |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [CyberArk Enterprise Password Vault (EPV) Events](../solutions/cyberark-enterprise-password-vault-(epv)-events.md) |
| **Connector Definition Files** | [template_CyberArkAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events/Data%20Connectors/template_CyberArkAMA.json) |

CyberArk Privilege Access Manager generates an xml Syslog message for every action taken against the Vault.  The PAM will send the xml messages through the Microsoft Sentinel.xsl translator to be converted into CEF standard format and sent to a syslog staging server of your choice (syslog-ng, rsyslog). The Log Analytics agent installed on your syslog staging server will import the messages into Microsoft Log Analytics. Refer to the [CyberArk documentation](https://docs.cyberark.com/privilege-cloud-standard/Latest/en/Content/Privilege%20Cloud/privCloud-connect-siem.htm) for more guidance on SIEM integrations.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Forward Common Event Format (CEF) logs to Syslog agent**

  On the EPV configure the dbparm.ini to send Syslog messages in CEF format to the proxy machine. Make sure you to send the logs to port 514 TCP on the machines IP address.

  **Step C. Validate connection**

  Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

 1. Make sure that you have Python on your machine using the following command: python -version

2. You must have elevated permissions (sudo) on your machine
  - **Run the following command to validate your connectivity:**: `sudo wget -O Sentinel_AMA_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/Syslog/Sentinel_AMA_troubleshoot.py&&sudo python Sentinel_AMA_troubleshoot.py --cef`

**2. Secure your machine**

Make sure to configure the machines security according to your organizations security policy


[Learn more >](https://aka.ms/SecureCEF)

[← Back to Connectors Index](../connectors-index.md)
