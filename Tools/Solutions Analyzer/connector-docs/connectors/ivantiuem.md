# [Deprecated] Ivanti Unified Endpoint Management

| | |
|----------|-------|
| **Connector ID** | `IvantiUEM` |
| **Publisher** | Ivanti |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Ivanti Unified Endpoint Management](../solutions/ivanti-unified-endpoint-management.md) |
| **Connector Definition Files** | [Ivanti_UEM_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ivanti%20Unified%20Endpoint%20Management/Data%20Connectors/Ivanti_UEM_Syslog.json) |

The [Ivanti Unified Endpoint Management](https://www.ivanti.com/products/unified-endpoint-manager) data connector provides the capability to ingest [Ivanti UEM Alerts](https://help.ivanti.com/ld/help/en_US/LDMS/11.0/Windows/alert-c-monitoring-overview.htm) into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**IvantiUEMEvent**](https://aka.ms/sentinel-ivantiuem-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:** This data connector has been developed using Ivanti Unified Endpoint Management Release 2021.1 Version 11.0.3.374

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Server where the Ivanti Unified Endpoint Management Alerts are forwarded.

> Logs from Ivanti Unified Endpoint Management Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

**2. Configure Ivanti Unified Endpoint Management alert forwarding.**

[Follow the instructions](https://help.ivanti.com/ld/help/en_US/LDMS/11.0/Windows/alert-t-define-action.htm) to set up Alert Actions to send logs to syslog server.

[← Back to Connectors Index](../connectors-index.md)
