# Vectra AI Detect

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Vectra AI |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vectra.ai/support](https://www.vectra.ai/support) |
| **Categories** | domains |
| **First Published** | 2022-05-24 |
| **Last Updated** | 2023-04-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Vectra AI Detect via Legacy Agent](../connectors/aivectradetect.md)

**Publisher:** Vectra AI

### [[Deprecated] Vectra AI Detect via AMA](../connectors/aivectradetectama.md)

**Publisher:** Vectra AI

The AI Vectra Detect connector allows users to connect Vectra Detect logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives users more insight into their organization's network and improves their security operation capabilities.

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

  **Step B. Forward AI Vectra Detect logs to Syslog agent in CEF format**

  Configure Vectra (X Series) Agent to forward Syslog messages in CEF format to your Microsoft Sentinel workspace via the Syslog agent.

From the Vectra UI, navigate to Settings > Notifications and Edit Syslog configuration. Follow below instructions to set up the connection:

- Add a new Destination (which is the host where the Microsoft Sentinel Syslog Agent is running)

- Set the Port as **514**

- Set the Protocol as **UDP**

- Set the format to **CEF**

- Set Log types (Select all log types available)

- Click on **Save**

User can click the **Test** button to force send some test events.

 For more information, refer to Cognito Detect Syslog Guide which can be downloaded from the ressource page in Detect UI.

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
| **Connector Definition Files** | [template_AIVectraDetectAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Data%20Connectors/template_AIVectraDetectAma.json) |

[→ View full connector details](../connectors/aivectradetectama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Vectra AI Detect via AMA](../connectors/aivectradetectama.md), [[Deprecated] Vectra AI Detect via Legacy Agent](../connectors/aivectradetect.md) |

[← Back to Solutions Index](../solutions-index.md)
