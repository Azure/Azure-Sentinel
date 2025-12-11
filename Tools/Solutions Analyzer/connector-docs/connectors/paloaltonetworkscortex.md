# Palo Alto Networks Cortex XDR

| | |
|----------|-------|
| **Connector ID** | `PaloAltoNetworksCortex` |
| **Publisher** | Palo Alto Networks |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Palo Alto - XDR (Cortex)](../solutions/palo-alto---xdr-(cortex).md) |
| **Connector Definition Files** | [Connector_PaloAlto_XDR_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20-%20XDR%20%28Cortex%29/Data%20Connectors/Connector_PaloAlto_XDR_CEF.json) |

The Palo Alto Networks Cortex XDR connector gives you an easy way to connect to your Cortex XDR logs with Microsoft Sentinel. This increases the visibility of your endpoint security. It will give you better ability to monitor your resources by creating custom Workbooks, analytics rules, Incident investigation, and evidence gathering.

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
**2. Forward Palo Alto Networks (Cortex) logs to Syslog agent**

> 1. Go to [Cortex Settings and Configurations](https://inspira.xdr.in.paloaltonetworks.com/configuration/external-alerting) and Click to add New Server under External Applications.

> 2. Then specify the name and Give public IP of your syslog server in Destination. 

> 3. Give Port number as 514 and from Facility field select FAC_SYSLOG from dropdown. 

> 4. Select Protocol as UDP and hit Create.

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
