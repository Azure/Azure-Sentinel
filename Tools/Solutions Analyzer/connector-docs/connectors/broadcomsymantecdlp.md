# [Deprecated] Broadcom Symantec DLP via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `BroadcomSymantecDLP` |
| **Publisher** | Broadcom |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Broadcom SymantecDLP](../solutions/broadcom-symantecdlp.md) |
| **Connector Definition Files** | [Connector_Syslog_SymantecDLP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP/Data%20Connectors/Connector_Syslog_SymantecDLP.json) |

The [Broadcom Symantec Data Loss Prevention (DLP)](https://www.broadcom.com/products/cyber-security/information-protection/data-loss-prevention) connector allows you to easily connect your Symantec DLP with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization’s information, where it travels, and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias SymantecDLP and load the function code or click [here](https://aka.ms/sentinel-symantecdlp-parser). The function usually takes 10-15 minutes to activate after solution installation/update.

**1. Linux Syslog agent configuration**

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Microsoft Sentinel.

> Notice that the data from all regions will be stored in the selected workspace
**1.1 Select or create a Linux machine**

  Select or create a Linux machine that Microsoft Sentinel will use as the proxy between your security solution and Microsoft Sentinel this machine can be on your on-prem environment, Azure or other clouds.

  **1.2 Install the CEF collector on the Linux machine**

  Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Microsoft Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP.

> 1. Make sure that you have Python on your machine using the following command: python –version.

> 2. You must have elevated permissions (sudo) on your machine.
  - **Run the following command to install and apply the CEF collector:**: `sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`
**2. Forward Symantec DLP logs to a Syslog agent**

Configure Symantec DLP to forward Syslog messages in CEF format to your Microsoft Sentinel workspace via the Syslog agent.
1. [Follow these instructions](https://knowledge.broadcom.com/external/article/159509/generating-syslog-messages-from-data-los.html) to configure the Symantec DLP to forward syslog
2. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

**3. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

>It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

> 1. Make sure that you have Python on your machine using the following command: python –version

>2. You must have elevated permissions (sudo) on your machine
- **Run the following command to validate your connectivity:**: `sudo wget -O cef_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py  {0}`

**4. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

[← Back to Connectors Index](../connectors-index.md)
