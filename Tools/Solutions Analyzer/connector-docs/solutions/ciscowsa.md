# CiscoWSA

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Cisco Web Security Appliance](../connectors/ciscowsa.md)

**Publisher:** Cisco

[Cisco Web Security Appliance (WSA)](https://www.cisco.com/c/en/us/products/security/web-security-appliance/index.html) data connector provides the capability to ingest [Cisco WSA Access Logs](https://www.cisco.com/c/en/us/td/docs/security/wsa/wsa_14-0/User-Guide/b_WSA_UserGuide_14_0/b_WSA_UserGuide_11_7_chapter_010101.html) into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**CiscoWSAEvent**](https://aka.ms/sentinel-CiscoWSA-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:** This data connector has been developed using AsyncOS 14.0 for Cisco Web Security Appliance

**1. Configure Cisco Web Security Appliance to forward logs via Syslog to remote server where you will install the agent.**

[Follow these steps](https://www.cisco.com/c/en/us/td/docs/security/esa/esa14-0/user_guide/b_ESA_Admin_Guide_14-0/b_ESA_Admin_Guide_12_1_chapter_0100111.html#con_1134718) to configure Cisco Web Security Appliance to forward logs via Syslog

>**NOTE:** Select **Syslog Push** as a Retrieval Method.

**2. Install and onboard the agent for Linux or Windows**

Install the agent on the Server to which the logs will be forwarded.

> Logs on Linux or Windows servers are collected by **Linux** or **Windows** agents.
**Choose where to install the Linux agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**Choose where to install the Windows agent:**

**Install agent on Azure Windows Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install/configure: InstallAgentOnVirtualMachine**

  **Install agent on a non-Azure Windows Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install/configure: InstallAgentOnNonAzure**

**3. Check logs in Microsoft Sentinel**

Open Log Analytics to check if the logs are received using the Syslog schema.

>**NOTE:** It may take up to 15 minutes before new logs will appear in Syslog table.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_WSA_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Data%20Connectors/Connector_WSA_Syslog.json) |

[→ View full connector details](../connectors/ciscowsa.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Cisco Web Security Appliance](../connectors/ciscowsa.md) |

[← Back to Solutions Index](../solutions-index.md)
