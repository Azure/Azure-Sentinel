# F5 Networks

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | F5 |
| **Support Tier** | Partner |
| **Support Link** | [https://www.f5.com/services/support](https://www.f5.com/services/support) |
| **Categories** | domains |
| **First Published** | 2022-05-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20Networks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20Networks) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] F5 Networks via Legacy Agent](../connectors/f5.md)

**Publisher:** F5 Networks

### [[Deprecated] F5 Networks via AMA](../connectors/f5ama.md)

**Publisher:** F5 Networks

The F5 firewall connector allows you to easily connect your F5 logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

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

  **Step B. Forward Common Event Format (CEF) logs to Syslog agent**

  Configure F5 to forward Syslog messages in CEF format to your Microsoft Sentinel workspace via the Syslog agent.

Go to [F5 Configuring Application Security Event Logging](https://aka.ms/asi-syslog-f5-forwarding), follow the instructions to set up remote logging, using the following guidelines:

1.  Set the  **Remote storage type**  to CEF.
2.  Set the  **Protocol setting**  to UDP.
3.  Set the  **IP address**  to the Syslog server IP address.
4.  Set the  **port number**  to 514, or the port your agent uses.
5.  Set the  **facility**  to the one that you configured in the Syslog agent (by default, the agent sets this to local4).
6.  You can set the  **Maximum Query String Size**  to be the same as you configured.

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
| **Connector Definition Files** | [template_F5NetworksAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20Networks/Data%20Connectors/template_F5NetworksAMA.json) |

[→ View full connector details](../connectors/f5ama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] F5 Networks via AMA](../connectors/f5ama.md), [[Deprecated] F5 Networks via Legacy Agent](../connectors/f5.md) |

[← Back to Solutions Index](../solutions-index.md)
