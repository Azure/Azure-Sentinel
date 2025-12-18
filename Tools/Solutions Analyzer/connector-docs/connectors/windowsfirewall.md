# Windows Firewall

| | |
|----------|-------|
| **Connector ID** | `WindowsFirewall` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`WindowsFirewall`](../tables-index.md#windowsfirewall) |
| **Used in Solutions** | [Windows Firewall](../solutions/windows-firewall.md) |
| **Connector Definition Files** | [Windows%20Firewall.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall/Data%20Connectors/Windows%20Firewall.JSON) |

Windows Firewall is a Microsoft Windows application that filters information coming to your system from the Internet and blocking potentially harmful programs. The software blocks most programs from communicating through the firewall. Users simply add a program to the list of allowed programs to allow it to communicate through the firewall. When using a public network, Windows Firewall can also secure the system by blocking all unsolicited attempts to connect to your computer. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2219791&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Solutions** (ResourceGroup): [read and write permissions](https://docs.microsoft.com/azure/role-based-access-control/built-in-roles#log-analytics-contributor).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Download and install the agent**

>  Windows Firewall logs are collected only from **Windows** agents.
**Choose where to install the agent:**

**Install agent on Azure Windows Virtual Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install/configure: InstallAgentOnVirtualMachine**

  **Install agent on non-Azure Windows Machine**

  Select the machine to install the agent and then click **Connect**.
  - **Install/configure: InstallAgentOnNonAzure**

**2. Install Windows Firewall solution**
- Install solution: WindowsFirewall

[← Back to Connectors Index](../connectors-index.md)
