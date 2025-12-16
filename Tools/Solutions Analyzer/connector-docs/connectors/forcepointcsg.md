# [Deprecated] Forcepoint CSG via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `ForcepointCSG` |
| **Publisher** | Forcepoint |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Forcepoint CSG](../solutions/forcepoint-csg.md) |
| **Connector Definition Files** | [ForcepointCloudSecurityGateway.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG/Data%20Connectors/ForcepointCloudSecurityGateway.json) |

Forcepoint Cloud Security Gateway is a converged cloud security service that provides visibility, control, and threat protection for users and data, wherever they are. For more information visit: https://www.forcepoint.com/product/cloud-security-gateway

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Linux Syslog agent configuration**

This integration requires the Linux Syslog agent to collect your Forcepoint Cloud Security Gateway Web/Email logs on port 514 TCP as Common Event Format (CEF) and forward them to Microsoft Sentinel.
- **Your Data Connector Syslog Agent Installation Command is:**: `sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`

**2. Implementation options**

The integration is made available with two implementations options.
**2.1  Docker Implementation**

  Leverages docker images where the integration component is already installed with all necessary dependencies.

Follow the instructions provided in the Integration Guide linked below.

[Integration Guide >](https://frcpnt.com/csg-sentinel)

  **2.2  Traditional Implementation**

  Requires the manual deployment of the integration component inside a clean Linux machine.

Follow the instructions provided in the Integration Guide  linked below.

[Integration Guide >](https://frcpnt.com/csg-sentinel)
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


[Learn more >](https://aka.ms/SecureCEF).

[← Back to Connectors Index](../connectors-index.md)
