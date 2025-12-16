# Fortinet FortiGate Next-Generation Firewall connector for Microsoft Sentinel

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-08-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Fortinet via Legacy Agent](../connectors/fortinet.md)

**Publisher:** Fortinet

### [[Deprecated] Fortinet via AMA](../connectors/fortinetama.md)

**Publisher:** Fortinet

The Fortinet firewall connector allows you to easily connect your Fortinet logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Forward Fortinet logs to Syslog agent**

  Set your Fortinet to send Syslog messages in CEF format to the proxy machine. Make sure you to send the logs to port 514 TCP on the machine’s IP address.


Copy the CLI commands below and:
-   Replace "server &lt;ip address&gt;" with the Syslog agent's IP address.
-   Set the "&lt;facility_name&gt;" to use the facility you configured in the Syslog agent (by default, the agent sets this to local4).
-   Set the Syslog port to 514, the port your agent uses.
-   To enable CEF format in early FortiOS versions, you may need to run the command "set csv disable".

For more information, go to the  [Fortinet Document Library](https://aka.ms/asi-syslog-fortinet-fortinetdocumentlibrary), choose your version, and use the "Handbook" and "Log Message Reference" PDFs.

[Learn more >](https://aka.ms/CEF-Fortinet)
  - **Set up the connection using the CLI to run the following commands:**: `config log syslogd setting
    set status enable
set format cef
set port 514
set server <ip_address_of_Receiver>
end`

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
| **Connector Definition Files** | [template_Fortinet-FortiGateAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/template_Fortinet-FortiGateAma.json) |

[→ View full connector details](../connectors/fortinetama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Fortinet via AMA](../connectors/fortinetama.md), [[Deprecated] Fortinet via Legacy Agent](../connectors/fortinet.md) |

[← Back to Solutions Index](../solutions-index.md)
