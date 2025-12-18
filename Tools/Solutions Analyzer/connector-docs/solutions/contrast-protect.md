# Contrast Protect

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Contrast Protect |
| **Support Tier** | Partner |
| **Support Link** | [https://docs.contrastsecurity.com/](https://docs.contrastsecurity.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Contrast Protect via Legacy Agent](../connectors/contrastprotect.md)

**Publisher:** Contrast Security

### [[Deprecated] Contrast Protect via AMA](../connectors/contrastprotectama.md)

**Publisher:** Contrast Security

Contrast Protect mitigates security threats in production applications with runtime protection and observability.  Attack event results (blocked, probed, suspicious...) and other information can be sent to Microsoft Microsoft Sentinel to blend with security information from other systems.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Microsoft Sentinel.

> Notice that the data from all regions will be stored in the selected workspace
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Forward Common Event Format (CEF) logs to Syslog agent**

  Configure the Contrast Protect agent to forward events to syslog as described here: https://docs.contrastsecurity.com/en/output-to-syslog.html. Generate some attack events for your application.

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
| **Connector Definition Files** | [template_ContrastProtectAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Data%20Connectors/template_ContrastProtectAMA.json) |

[→ View full connector details](../connectors/contrastprotectama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Contrast Protect via AMA](../connectors/contrastprotectama.md), [[Deprecated] Contrast Protect via Legacy Agent](../connectors/contrastprotect.md) |

[← Back to Solutions Index](../solutions-index.md)
