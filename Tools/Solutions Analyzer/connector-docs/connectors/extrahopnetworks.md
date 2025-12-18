# [Deprecated] ExtraHop Reveal(x) via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `ExtraHopNetworks` |
| **Publisher** | ExtraHop Networks |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [ExtraHop Reveal(x)](../solutions/extrahop-reveal(x).md) |
| **Connector Definition Files** | [template_ExtraHopNetworks.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29/Data%20Connectors/template_ExtraHopNetworks.json) |

The ExtraHop Reveal(x) data connector enables you to easily connect your Reveal(x) system with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. This integration gives you the ability to gain insight into your organization's network and improve your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **ExtraHop**: ExtraHop Discover or Command appliance with firmware version 7.8 or later with a user account that has Unlimited (administrator) privileges.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Linux Syslog agent configuration**

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Microsoft Sentinel.

> Notice that the data from all regions will be stored in the selected workspace
**1.1 Select or create a Linux machine**

  Select or create a Linux machine that Microsoft Sentinel will use as the proxy between your security solution and Microsoft Sentinel this machine can be on your on-prem environment, Azure or other clouds.

  **1.2 Install the CEF collector on the Linux machine**

  Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Microsoft Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP.

> 1. Make sure that you have Python on your machine using the following command: python --version.

> 2. You must have elevated permissions (sudo) on your machine.
  - **Run the following command to install and apply the CEF collector:**: `sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`
**2. Forward ExtraHop Networks logs to Syslog agent**

1.  Set your security solution to send Syslog messages in CEF format to the proxy machine. Make sure to send the logs to port 514 TCP on the machine IP address.
2. Follow the directions to install the [ExtraHop Detection SIEM Connector bundle](https://aka.ms/asi-syslog-extrahop-forwarding) on your Reveal(x) system. The SIEM Connector is required for this integration.
3. Enable the trigger for **ExtraHop Detection SIEM Connector - CEF**
4. Update the trigger with the ODS syslog targets you created 
5. The Reveal(x) system formats syslog messages in Common Event Format (CEF) and then sends data to Microsoft Sentinel.

**3. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

>It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

> 1. Make sure that you have Python on your machine using the following command: python --version

>2. You must have elevated permissions (sudo) on your machine
- **Run the following command to validate your connectivity:**: `sudo wget -O cef_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py  {0}`

**4. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

[← Back to Connectors Index](../connectors-index.md)
