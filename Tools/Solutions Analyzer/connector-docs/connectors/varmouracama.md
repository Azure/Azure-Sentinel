# [Deprecated] vArmour Application Controller via AMA

| | |
|----------|-------|
| **Connector ID** | `vArmourACAma` |
| **Publisher** | vArmour |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [vArmour Application Controller](../solutions/varmour-application-controller.md) |
| **Connector Definition Files** | [template_vArmour_AppControllerAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller/Data%20Connectors/template_vArmour_AppControllerAMA.json) |

vArmour reduces operational risk and increases cyber resiliency by visualizing and controlling application relationships across the enterprise. This vArmour connector enables streaming of Application Controller Violation Alerts into Microsoft Sentinel, so you can take advantage of search & correlation, alerting, & threat intelligence enrichment for each log.

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

  **Step B. Configure the vArmour Application Controller to forward Common Event Format (CEF) logs to the Syslog agent**

  Send Syslog messages in CEF format to the proxy machine. Make sure you to send the logs to port 514 TCP on the machine's IP address.
**1 Download the vArmour Application Controller user guide**

    Download the user guide from https://support.varmour.com/hc/en-us/articles/360057444831-vArmour-Application-Controller-6-0-User-Guide.

    **2 Configure the Application Controller to Send Policy Violations**

    In the user guide - refer to "Configuring Syslog for Monitoring and Violations" and follow steps 1 to 3.
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
