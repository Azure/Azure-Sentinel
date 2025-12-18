# [Deprecated] Zscaler Private Access

| | |
|----------|-------|
| **Connector ID** | `ZscalerPrivateAccess` |
| **Publisher** | Zscaler |
| **Tables Ingested** | [`ZPA_CL`](../tables-index.md#zpa_cl) |
| **Used in Solutions** | [Zscaler Private Access (ZPA)](../solutions/zscaler-private-access-(zpa).md) |
| **Connector Definition Files** | [Connector_LogAnalytics_agent_Zscaler_ZPA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Data%20Connectors/Connector_LogAnalytics_agent_Zscaler_ZPA.json) |

The [Zscaler Private Access (ZPA)](https://help.zscaler.com/zpa/what-zscaler-private-access) data connector provides the capability to ingest [Zscaler Private Access events](https://help.zscaler.com/zpa/log-streaming-service) into Microsoft Sentinel. Refer to [Zscaler Private Access documentation](https://help.zscaler.com/zpa) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected. [Follow these steps](https://aka.ms/sentinel-ZscalerPrivateAccess-parser) to create the Kusto Functions alias, **ZPAEvent**

>**NOTE:** This data connector has been developed using Zscaler Private Access version: 21.67.1

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Server where the Zscaler Private Access logs are forwarded.

> Logs from Zscaler Private Access Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

Follow the configuration steps below to get Zscaler Private Access logs into Microsoft Sentinel. Refer to the [Azure Monitor Documentation](https://docs.microsoft.com/azure/azure-monitor/agents/data-sources-json) for more details on these steps.
Zscaler Private Access logs are delivered via Log Streaming Service (LSS). Refer to [LSS documentation](https://help.zscaler.com/zpa/about-log-streaming-service) for detailed information
1. Configure [Log Receivers](https://help.zscaler.com/zpa/configuring-log-receiver). While configuring a Log Receiver, choose **JSON** as **Log Template**.
2. Download config file [zpa.conf](https://aka.ms/sentinel-ZscalerPrivateAccess-conf) 
		wget -v https://aka.ms/sentinel-zscalerprivateaccess-conf -O zpa.conf
3. Login to the server where you have installed Azure Log Analytics agent.
4. Copy zpa.conf to the /etc/opt/microsoft/omsagent/**workspace_id**/conf/omsagent.d/ folder.
5. Edit zpa.conf as follows:

	 a. specify port which you have set your Zscaler Log Receivers to forward logs to (line 4)

	 b. zpa.conf uses the port **22033** by default. Ensure this port is not being used by any other source on your server

	 c. If you would like to change the default port for **zpa.conf** make sure that it should not get conflict with default AMA agent ports I.e.(For example CEF uses TCP port **25226** or **25224**) 

	 d. replace **workspace_id** with real value of your Workspace ID (lines 14,15,16,19)
5. Save changes and restart the Azure Log Analytics agent for Linux service with the following command:
		sudo /opt/microsoft/omsagent/bin/service_control restart
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
