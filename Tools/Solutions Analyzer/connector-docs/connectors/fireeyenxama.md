# [Deprecated] FireEye Network Security (NX) via AMA

| | |
|----------|-------|
| **Connector ID** | `FireEyeNXAma` |
| **Publisher** | FireEye |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [FireEye Network Security](../solutions/fireeye-network-security.md) |
| **Connector Definition Files** | [template_FireEyeNX_CEFAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security/Data%20Connectors/template_FireEyeNX_CEFAMA.json) |

The [FireEye Network Security (NX)](https://www.fireeye.com/products/network-security.html) data connector provides the capability to ingest FireEye Network Security logs into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**FireEyeNXEvent**](https://aka.ms/sentinel-FireEyeNX-parser) which is deployed with the Microsoft Sentinel Solution.
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Configure FireEye NX to send logs using CEF**

  Complete the following steps to send data using CEF:

2.1. Log into the FireEye appliance with an administrator account

2.2. Click **Settings**

2.3. Click **Notifications**

Click **rsyslog**

2.4. Check the **Event type** check box

2.5. Make sure Rsyslog settings are:

- Default format: CEF

- Default delivery: Per event

- Default send as: Alert

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
