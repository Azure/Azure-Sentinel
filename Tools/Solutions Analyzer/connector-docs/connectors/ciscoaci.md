# [Deprecated] Cisco Application Centric Infrastructure

| | |
|----------|-------|
| **Connector ID** | `CiscoACI` |
| **Publisher** | Cisco |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Cisco ACI](../solutions/cisco-aci.md) |
| **Connector Definition Files** | [CiscoACI_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ACI/Data%20Connectors/CiscoACI_Syslog.json) |

[Cisco Application Centric Infrastructure (ACI)](https://www.cisco.com/c/en/us/solutions/collateral/data-center-virtualization/application-centric-infrastructure/solution-overview-c22-741487.html) data connector provides the capability to ingest [Cisco ACI logs](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/all/syslog/guide/b_ACI_System_Messages_Guide/m-aci-system-messages-reference.html) into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**CiscoACIEvent**](https://aka.ms/sentinel-CiscoACI-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:**  This data connector has been developed using Cisco ACI Release 1.x

**1. Configure Cisco ACI system sending logs via Syslog to remote server where you will install the agent.**

[Follow these steps](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/1-x/basic-config/b_ACI_Config_Guide/b_ACI_Config_Guide_chapter_010.html#d2933e4611a1635) to configure Syslog Destination, Destination Group, and Syslog Source.

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

[← Back to Connectors Index](../connectors-index.md)
