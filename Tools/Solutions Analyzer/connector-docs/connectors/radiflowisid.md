# Radiflow iSID via AMA

| | |
|----------|-------|
| **Connector ID** | `RadiflowIsid` |
| **Publisher** | Radiflow |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Radiflow](../solutions/radiflow.md) |
| **Connector Definition Files** | [RadiflowIsid.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Data%20Connectors/RadiflowIsid.json) |

iSID enables non-disruptive monitoring of distributed ICS networks for changes in topology and behavior, using multiple security packages, each offering a unique capability pertaining to a specific type of network activity

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**RadiflowEvent**] which is deployed with the Microsoft Sentinel Solution.
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade.

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule).

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy._

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine.

  **Step B. Configure iSID to send logs using CEF**

  Configure log forwarding using CEF:

1. Navigate to the **System Notifications** section of the Configuration menu.

2. Under Syslog, select **+Add**.

3. In the **New Syslog Server** dialog specify the name, remote server **IP**, **Port**, **Transport** and select **Format** - **CEF**.

4. Press **Apply** to exit the **Add Syslog dialog**.

  **Step C. Validate connection**

  Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

 1. Make sure that you have Python on your machine using the following command: python --version

2. You must have elevated permissions (sudo) on your machine
  - **Run the following command to validate your connectivity:**: `sudo wget -O Sentinel_AMA_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/Syslog/Sentinel_AMA_troubleshoot.py&&sudo python Sentinel_AMA_troubleshoot.py --cef`

**2. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

[← Back to Connectors Index](../connectors-index.md)
