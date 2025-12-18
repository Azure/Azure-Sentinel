# Delinea Secret Server

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Delinea |
| **Support Tier** | Partner |
| **Support Link** | [https://delinea.com/support/](https://delinea.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Delinea Secret Server via AMA](../connectors/delineasecretserverama.md)

**Publisher:** Delinea, Inc

### [[Deprecated] Delinea Secret Server via Legacy Agent](../connectors/delineasecretserver-cef.md)

**Publisher:** Delinea, Inc

Common Event Format (CEF) from Delinea Secret Server 

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Delinea Secret Server**: must be configured to export logs via Syslog 

   [Learn more about configure Secret Server](https://thy.center/ss/link/syslog)

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
  - **Run the following command to install and apply the CEF collector:**: `sudo wget https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`
**2. Forward Common Event Format (CEF) logs to Syslog agent**

Set your security solution to send Syslog messages in CEF format to the proxy machine. Make sure you to send the logs to port 514 TCP on the machine's IP address.

**3. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

>It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

> 1. Make sure that you have Python on your machine using the following command: python -version

>2. You must have elevated permissions (sudo) on your machine
- **Run the following command to validate your connectivity:**: `sudo wget https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py  {0}`

**4. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [DelineaSecretServer_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server/Data%20Connectors/DelineaSecretServer_CEF.json) |

[→ View full connector details](../connectors/delineasecretserver-cef.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Delinea Secret Server via AMA](../connectors/delineasecretserverama.md), [[Deprecated] Delinea Secret Server via Legacy Agent](../connectors/delineasecretserver-cef.md) |

[← Back to Solutions Index](../solutions-index.md)
