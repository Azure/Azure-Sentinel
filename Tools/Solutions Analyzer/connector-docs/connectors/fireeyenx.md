# [Deprecated] FireEye Network Security (NX) via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `FireEyeNX` |
| **Publisher** | FireEye |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [FireEye Network Security](../solutions/fireeye-network-security.md) |
| **Connector Definition Files** | [Connector_FireEyeNX_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security/Data%20Connectors/Connector_FireEyeNX_CEF.json) |

The [FireEye Network Security (NX)](https://www.fireeye.com/products/network-security.html) data connector provides the capability to ingest FireEye Network Security logs into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**FireEyeNXEvent**](https://aka.ms/sentinel-FireEyeNX-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:** This data connector has been developed using FEOS release v9.0

**1. Linux Syslog agent configuration**

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Microsoft Sentinel.

> Notice that the data from all regions will be stored in the selected workspace
**1.1 Select or create a Linux machine**

  Select or create a Linux machine that Microsoft Sentinel will use as the proxy between your security solution and Microsoft Sentinel this machine can be on your on-prem environment, Azure or other clouds.

  **1.2 Install the CEF collector on the Linux machine**

  Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Microsoft Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP.

> 1. Make sure that you have Python on your machine using the following command: python -version.

> 2. You must have elevated permissions (sudo) on your machine.
  - **Run the following command to install and apply the CEF collector:**: `sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`
**2.  Configure FireEye NX to send logs using CEF**

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

**3. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

>It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

> 1. Make sure that you have Python on your machine using the following command: python -version

>2. You must have elevated permissions (sudo) on your machine
- **Run the following command to validate your connectivity:**: `sudo wget -O cef_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py  {0}`

**4. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

[← Back to Connectors Index](../connectors-index.md)
