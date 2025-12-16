# [Deprecated] Ubiquiti UniFi

| | |
|----------|-------|
| **Connector ID** | `UbiquitiUnifi` |
| **Publisher** | Ubiquiti |
| **Tables Ingested** | [`Ubiquiti_CL`](../tables-index.md#ubiquiti_cl) |
| **Used in Solutions** | [Ubiquiti UniFi](../solutions/ubiquiti-unifi.md) |
| **Connector Definition Files** | [Connector_Ubiquiti_agent.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Data%20Connectors/Connector_Ubiquiti_agent.json) |

The [Ubiquiti UniFi](https://www.ui.com/) data connector provides the capability to ingest [Ubiquiti UniFi firewall, dns, ssh, AP events](https://help.ui.com/hc/en-us/articles/204959834-UniFi-How-to-View-Log-Files) into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**UbiquitiAuditEvent**](https://aka.ms/sentinel-UbiquitiUnifi-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:** This data connector has been developed using Enterprise System Controller Release Version: 5.6.2 (Syslog)

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Server to which the Ubiquiti logs are forwarder from Ubiquiti device (e.g.remote syslog server)

> Logs from Ubiquiti Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

**2. Configure the logs to be collected**

Follow the configuration steps below to get Ubiquiti logs into Microsoft Sentinel. Refer to the [Azure Monitor Documentation](https://docs.microsoft.com/azure/azure-monitor/agents/data-sources-json) for more details on these steps.
1. Configure log forwarding on your Ubiquiti controller: 

	 i. Go to Settings > System Setting > Controller Configuration > Remote Logging and enable the Syslog and Debugging (optional) logs (Refer to [User Guide](https://dl.ui.com/guides/UniFi/UniFi_Controller_V5_UG.pdf) for detailed instructions).
2. Download config file [Ubiquiti.conf](https://aka.ms/sentinel-UbiquitiUnifi-conf).
3. Login to the server where you have installed Azure Log Analytics agent.
4. Copy Ubiquiti.conf to the /etc/opt/microsoft/omsagent/**workspace_id**/conf/omsagent.d/ folder.
5. Edit Ubiquiti.conf as follows:

	 i. specify port which you have set your Ubiquiti device to forward logs to (line 4)

	 ii. replace **workspace_id** with real value of your Workspace ID (lines 14,15,16,19)
5. Save changes and restart the Azure Log Analytics agent for Linux service with the following command:
		sudo /opt/microsoft/omsagent/bin/service_control restart
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
