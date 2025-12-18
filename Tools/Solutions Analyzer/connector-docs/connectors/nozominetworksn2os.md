# [Deprecated] Nozomi Networks N2OS via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `NozomiNetworksN2OS` |
| **Publisher** | Nozomi Networks |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [NozomiNetworks](../solutions/nozominetworks.md) |
| **Connector Definition Files** | [NozomiNetworksN2OS.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NozomiNetworks/Data%20Connectors/NozomiNetworksN2OS.json) |

The [Nozomi Networks](https://www.nozominetworks.com/) data connector provides the capability to ingest Nozomi Networks Events into Microsoft Sentinel. Refer to the Nozomi Networks [PDF documentation](https://www.nozominetworks.com/resources/data-sheets-brochures-learning-guides/) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**NozomiNetworksEvents**](https://aka.ms/sentinel-NozomiNetworks-parser) which is deployed with the Microsoft Sentinel Solution.

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

Follow these steps to configure Nozomi Networks device for sending Alerts, Audit Logs, Health Logs log via syslog in CEF format:

> 1. Log in to the Guardian console.

> 2. Navigate to Administration->Data Integration, press +Add and select the Common Event Format (CEF) from the drop down

> 3. Create New Endpoint using the appropriate host information and enable Alerts, Audit Logs, Health Logs for sending.

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
