# AI Vectra Stream via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `AIVectraStream` |
| **Publisher** | Vectra AI |
| **Tables Ingested** | [`VectraStream`](../tables-index.md#vectrastream), [`VectraStream_CL`](../tables-index.md#vectrastream_cl) |
| **Used in Solutions** | [Vectra AI Stream](../solutions/vectra-ai-stream.md) |
| **Connector Definition Files** | [Connector_VectraAI_Stream.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Data%20Connectors/Connector_VectraAI_Stream.json) |

The AI Vectra Stream connector allows to send Network Metadata collected by Vectra Sensors accross the Network and Cloud to Microsoft Sentinel

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Vectra AI Brain**: must be configured to export Stream metadata in JSON

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected **VectraStream** which is deployed with the Microsoft Sentinel Solution.

**1. Install and onboard the agent for Linux**

Install the Linux agent on sperate Linux instance.

> Logs are collected only from **Linux** agents.
**Choose where to install the Linux agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**2. Configure the logs to be collected**

Follow the configuration steps below to get Vectra Stream metadata into Microsoft Sentinel. The Log Analytics agent is leveraged to send custom JSON into Azure Monitor, enabling the storage of the metadata into a custom table. For more information, refer to the [Azure Monitor Documentation](https://docs.microsoft.com/azure/azure-monitor/agents/data-sources-json).
1. Download config file for the log analytics agent: VectraStream.conf (located in the Connector folder within the Vectra solution: https://aka.ms/sentinel-aivectrastream-conf).
2. Login to the server where you have installed Azure Log Analytics agent.
3. Copy VectraStream.conf to the /etc/opt/microsoft/omsagent/**workspace_id**/conf/omsagent.d/ folder.
4. Edit VectraStream.conf as follows:

	 i. configure an alternate port to send data to, if desired. Default port is 29009.

	 ii. replace **workspace_id** with real value of your Workspace ID.
5. Save changes and restart the Azure Log Analytics agent for Linux service with the following command:
		sudo /opt/microsoft/omsagent/bin/service_control restart
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Configure and connect Vectra AI Stream**

Configure Vectra AI Brain to forward Stream metadata in JSON format to your Microsoft Sentinel workspace via the Log Analytics Agent.

From the Vectra UI, navigate to Settings > Cognito Stream and Edit the destination configuration:

- Select Publisher: RAW JSON

- Set the server IP or hostname (which is the host which run the Log Analytics Agent)

- Set all the port to **29009** (this port can be modified if required)

- Save

- Set Log types (Select all log types available)

- Click on **Save**

[← Back to Connectors Index](../connectors-index.md)
