# Illusive Platform

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Illusive Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://illusive.com/support](https://illusive.com/support) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Illusive Platform via Legacy Agent](../connectors/illusiveattackmanagementsystem.md)

**Publisher:** illusive

### [[Deprecated] Illusive Platform via AMA](../connectors/illusiveattackmanagementsystemama.md)

**Publisher:** illusive

The Illusive Platform Connector allows you to share Illusive's attack surface analysis data and incident logs with Microsoft Sentinel and view this information in dedicated dashboards that offer insight into your organization's attack surface risk (ASM Dashboard) and track unauthorized lateral movement in your organization's network (ADS Dashboard).

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

  **Step B. Forward Illusive Common Event Format (CEF) logs to Syslog agent**

  1. Set your security solution to send Syslog messages in CEF format to the proxy machine. Make sure you to send the logs to port 514 TCP on the machine's IP address.
> 2. Log onto the Illusive Console, and navigate to Settings->Reporting.
> 3. Find Syslog Servers
> 4. Supply the following information:
>> 1. Host name: Linux Syslog agent IP address or FQDN host name
>> 2. Port: 514
>> 3. Protocol: TCP
>> 4. Audit messages: Send audit messages to server
> 5. To add the syslog server, click Add.
> 6. For more information about how to add a new syslog server in the Illusive platform, please find the Illusive Networks Admin Guide in here: https://support.illusivenetworks.com/hc/en-us/sections/360002292119-Documentation-by-Version

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
| **Connector Definition Files** | [template_IllusivePlatformAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform/Data%20Connectors/template_IllusivePlatformAMA.json) |

[→ View full connector details](../connectors/illusiveattackmanagementsystemama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Illusive Platform via AMA](../connectors/illusiveattackmanagementsystemama.md), [[Deprecated] Illusive Platform via Legacy Agent](../connectors/illusiveattackmanagementsystem.md) |

[← Back to Solutions Index](../solutions-index.md)
