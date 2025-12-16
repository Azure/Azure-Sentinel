# [Deprecated] AI Analyst Darktrace via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `Darktrace` |
| **Publisher** | Darktrace |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [AI Analyst Darktrace](../solutions/ai-analyst-darktrace.md) |
| **Connector Definition Files** | [AIA-Darktrace.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AI%20Analyst%20Darktrace/Data%20Connectors/AIA-Darktrace.json) |

The Darktrace connector lets users connect Darktrace Model Breaches in real-time with Microsoft Sentinel, allowing creation of custom Dashboards, Workbooks, Notebooks and Custom Alerts to improve investigation.  Microsoft Sentinel's enhanced visibility into Darktrace logs enables monitoring and mitigation of security threats.

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

  Select or create a Linux machine that Microsoft Sentinel will use as the proxy between your security solution and Microsoft Sentinel this machine can be on your on-prem environment, Azure or other clouds.

  **1.2 Install the CEF collector on the Linux machine**

  Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Microsoft Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP.

> 1. Make sure that you have Python on your machine using the following command: python -version.

> 2. You must have elevated permissions (sudo) on your machine.
  - **Run the following command to install and apply the CEF collector:**: `sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`
**2. Forward Common Event Format (CEF) logs to Syslog agent**

Configure Darktrace to forward Syslog messages in CEF format to your Azure workspace via the Syslog agent. 

 1) Within the Darktrace Threat Visualizer, navigate to the System Config page in the main menu under Admin. 

  2) From the left-hand menu, select Modules and choose Microsoft Sentinel from the available Workflow Integrations.\n 3) A configuration window will open. Locate Microsoft Sentinel Syslog CEF and click New to reveal the configuration settings, unless already exposed. 

 4) In the Server configuration field, enter the location of the log forwarder and optionally modify the communication port. Ensure that the port selected is set to 514 and is allowed by any intermediary firewalls. 

 5) Configure any alert thresholds, time offsets or additional settings as required. 

 6) Review any additional configuration options you may wish to enable that alter the Syslog syntax.

 7) Enable Send Alerts and save your changes.

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

[← Back to Connectors Index](../connectors-index.md)
