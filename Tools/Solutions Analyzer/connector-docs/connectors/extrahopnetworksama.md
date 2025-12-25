# [Deprecated] ExtraHop Reveal(x) via AMA

| | |
|----------|-------|
| **Connector ID** | `ExtraHopNetworksAma` |
| **Publisher** | ExtraHop Networks |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [ExtraHop Reveal(x)](../solutions/extrahop-reveal(x).md) |
| **Connector Definition Files** | [template_ExtraHopReveal%28x%29AMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29/Data%20Connectors/template_ExtraHopReveal%28x%29AMA.json) |

The ExtraHop Reveal(x) data connector enables you to easily connect your Reveal(x) system with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. This integration gives you the ability to gain insight into your organization's network and improve your security operation capabilities.

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

  **Step B. Forward ExtraHop Networks logs to Syslog agent**

  1.  Set your security solution to send Syslog messages in CEF format to the proxy machine. Make sure to send the logs to port 514 TCP on the machine IP address.
2. Follow the directions to install the [ExtraHop Detection SIEM Connector bundle](https://aka.ms/asi-syslog-extrahop-forwarding) on your Reveal(x) system. The SIEM Connector is required for this integration.
3. Enable the trigger for **ExtraHop Detection SIEM Connector - CEF**
4. Update the trigger with the ODS syslog targets you created 
5. The Reveal(x) system formats syslog messages in Common Event Format (CEF) and then sends data to Microsoft Sentinel.

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
