# Votiro

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Votiro |
| **Support Tier** | Partner |
| **Support Link** | [https://support.votiro.com/](https://support.votiro.com/) |
| **Categories** | domains |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Votiro](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Votiro) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Votiro Sanitization Engine Logs](../connectors/votiro.md)

**Publisher:** Votiro

The Votiro data connector allows you to easily connect your Votiro Event logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation.  Using Votiro on Microsoft Sentinel will provide you more insights into the sanitization results of files.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

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
**2. Forward Common Event Format (CEF) logs to Syslog agent**

Set Votiro Endpoints to send Syslog messages in CEF format to the Forwarder machine. Make sure you to send the logs to port 514 TCP on the Forwarder machine's IP address.

**3. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

>It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

> 1. Make sure that you have Python on your machine using the following command: python -version

>2. You must have elevated permissions (sudo) on your machine
- **Run the following command to validate your connectivity:**: `sudo wget  -O cef_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py  {0}`

**4. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [VotiroEvents.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Votiro/Data%20Connectors/VotiroEvents.json) |

[→ View full connector details](../connectors/votiro.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Votiro Sanitization Engine Logs](../connectors/votiro.md) |

[← Back to Solutions Index](../solutions-index.md)
