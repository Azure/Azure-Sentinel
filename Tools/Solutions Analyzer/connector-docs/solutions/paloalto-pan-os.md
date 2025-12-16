# PaloAlto-PAN-OS

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-08-09 |
| **Last Updated** | 2021-09-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Palo Alto Networks (Firewall) via Legacy Agent](../connectors/paloaltonetworks.md)

**Publisher:** Palo Alto Networks

### [[Deprecated] Palo Alto Networks (Firewall) via AMA](../connectors/paloaltonetworksama.md)

**Publisher:** Palo Alto Networks

The Palo Alto Networks firewall connector allows you to easily connect your Palo Alto Networks logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Forward Palo Alto Networks logs to Syslog agent**

  Configure Palo Alto Networks to forward Syslog messages in CEF format to your Microsoft Sentinel workspace via the Syslog agent.

Go to [configure Palo Alto Networks NGFW for sending CEF events.](https://aka.ms/sentinel-paloaltonetworks-readme)

Go to [Palo Alto CEF Configuration](https://aka.ms/asi-syslog-paloalto-forwarding)  and Palo Alto [Configure Syslog Monitoring](https://aka.ms/asi-syslog-paloalto-configure)  steps 2, 3, choose your version, and follow the instructions using the following guidelines:

1.  Set the Syslog server format to  **BSD**.

2.  The copy/paste operations from the PDF might change the text and insert random characters. To avoid this, copy the text to an editor and remove any characters that might break the log format before pasting it.

[Learn more >](https://aka.ms/CEFPaloAlto)

  **Step C. Validate connection**

  Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

 1. Make sure that you have Python on your machine using the following command: python -version

2. You must have elevated permissions (sudo) on your machine
  - **Run the following command to validate your connectivity:**: `sudo wget -O Sentinel_AMA_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/Syslog/Sentinel_AMA_troubleshoot.py&&sudo python Sentinel_AMA_troubleshoot.py --cef`

**2. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_PaloAltoNetworksAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Data%20Connectors/template_PaloAltoNetworksAMA.json) |

[→ View full connector details](../connectors/paloaltonetworksama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Palo Alto Networks (Firewall) via AMA](../connectors/paloaltonetworksama.md), [[Deprecated] Palo Alto Networks (Firewall) via Legacy Agent](../connectors/paloaltonetworks.md) |

[← Back to Solutions Index](../solutions-index.md)
