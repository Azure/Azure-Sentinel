# [Deprecated] Onapsis Platform

| | |
|----------|-------|
| **Connector ID** | `OnapsisPlatform` |
| **Publisher** | Onapsis |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Onapsis Platform](../solutions/onapsis-platform.md) |
| **Connector Definition Files** | [OnapsisPlatform.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Platform/Data%20Connectors/OnapsisPlatform.json) |

The Onapsis Connector allows you to export the alarms triggered in the Onapsis Platform into Microsoft Sentinel in real-time. This gives you the ability to monitor the activity on your SAP systems, identify incidents and respond to them quickly.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Linux Syslog agent configuration**

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Microsoft Sentinel.

> Notice that the data from all regions will be stored in the selected workspace
**1.1 Select or create a Linux machine**

  Select or create a Linux machine that Microsoft Sentinel will use as the proxy between your Onapsis Console and Microsoft Sentinel. This machine can be on your on-prem environment, Azure or other clouds.

  **1.2 Install the CEF collector on the Linux machine**

  Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Microsoft Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP.

> 1. Make sure that you have Python on your machine using the following command: python -version.

> 2. You must have elevated permissions (sudo) on your machine.
  - **Run the following command to install and apply the CEF collector:**: `sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`
**2. Forward Common Event Format (CEF) logs to Syslog agent**

Refer to the Onapsis in-product help to set up log forwarding to the Syslog agent.

> 1. Go to Setup > Third-party integrations > Defend Alarms and follow the instructions for Microsoft Sentinel.

> 2. Make sure your Onapsis Console can reach the proxy machine where the agent is installed - logs should be sent to port 514 using TCP.

**3. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

>It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

> 1. Make sure that you have Python on your machine using the following command: python -version

>2. You must have elevated permissions (sudo) on your machine
- **Run the following command to validate your connectivity:**: `sudo wget  -O cef_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py  {0}`

**4. Create Onapsis lookup function for incident enrichment**

[Follow these steps to get this Kusto function](https://aka.ms/sentinel-Onapsis-parser)

**5. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

[← Back to Connectors Index](../connectors-index.md)
