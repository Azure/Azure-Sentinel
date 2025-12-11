# Forcepoint CSG

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-05-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Forcepoint CSG via Legacy Agent](../connectors/forcepointcsg.md)

**Publisher:** Forcepoint

### [[Deprecated] Forcepoint CSG via AMA](../connectors/forcepointcsgama.md)

**Publisher:** Forcepoint

Forcepoint Cloud Security Gateway is a converged cloud security service that provides visibility, control, and threat protection for users and data, wherever they are. For more information visit: https://www.forcepoint.com/product/cloud-security-gateway

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

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine.

  **Step B. Implementation options**

  The integration is made available with two implementations options.
**1.  Docker Implementation**

    Leverages docker images where the integration component is already installed with all necessary dependencies.

Follow the instructions provided in the Integration Guide linked below.

[Integration Guide >](https://frcpnt.com/csg-sentinel)

    **2.  Traditional Implementation**

    Requires the manual deployment of the integration component inside a clean Linux machine.

Follow the instructions provided in the Integration Guide  linked below.

[Integration Guide >](https://frcpnt.com/csg-sentinel)
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


[Learn more >](https://aka.ms/SecureCEF).

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ForcepointCloudSecurityGatewayAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG/Data%20Connectors/template_ForcepointCloudSecurityGatewayAMA.json) |

[→ View full connector details](../connectors/forcepointcsgama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Forcepoint CSG via AMA](../connectors/forcepointcsgama.md), [[Deprecated] Forcepoint CSG via Legacy Agent](../connectors/forcepointcsg.md) |

[← Back to Solutions Index](../solutions-index.md)
