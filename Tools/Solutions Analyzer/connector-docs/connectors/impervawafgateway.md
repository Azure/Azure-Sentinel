# Imperva WAF Gateway

| | |
|----------|-------|
| **Connector ID** | `ImpervaWAFGateway` |
| **Publisher** | Imperva |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Imperva WAF Gateway](../solutions/imperva-waf-gateway.md) |
| **Connector Definition Files** | [Connector_Imperva_WAF_Gateway.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Imperva%20WAF%20Gateway/Data%20Connectors/Connector_Imperva_WAF_Gateway.json) |

The [Imperva](https://www.imperva.com) connector will allow you to quickly connect your Imperva WAF Gateway alerts to Azure Sentinel. This provides you additional insight into your organization's WAF traffic and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Linux Syslog agent configuration**

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Azure Sentinel.

> Notice that the data from all regions will be stored in the selected workspace
**1.1 Select or create a Linux machine**

  Select or create a Linux machine that Azure Sentinel will use as the proxy between your security solution and Azure Sentinel this machine can be on your on-prem environment, Azure or other clouds.

  **1.2 Install the CEF collector on the Linux machine**

  Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Azure Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP.

> 1. Make sure that you have Python on your machine using the following command: python -version.

> 2. You must have elevated permissions (sudo) on your machine.
  - **Run the following command to install and apply the CEF collector:**: `sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`
**2. Forward Common Event Format (CEF) logs to Syslog agent**

Set your security solution to send Syslog messages in CEF format to the proxy machine. Make sure you to send the logs to port 514 TCP on the machine's IP address.

**3. SecureSphere MX Configuration**

This connector requires an Action Interface and Action Set to be created on the Imperva SecureSphere MX.  [Follow the steps](https://community.imperva.com/blogs/craig-burlingame1/2020/11/13/steps-for-enabling-imperva-waf-gateway-alert) to create the requirements.
**3.1 Create the Action Interface**

  Create a new Action Interface that contains the required parameters to send WAF alerts to Azure Sentinel.

  **3.2 Create the Action Set**

  Create a new Action Set that uses the Action Interface configured.

  **3.3 Apply the Action Set**

  Apply the Action Set to any Security Policies you wish to have alerts for sent to Azure Sentinel.
**4. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.
**4.1 Check for logs in the past 5 minutes using the following command.

CommonSecurityLog | where DeviceVendor == "Imperva Inc." | where DeviceProduct == "WAF Gateway" | where TimeGenerated == ago(5m)**
**5. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

[← Back to Connectors Index](../connectors-index.md)
