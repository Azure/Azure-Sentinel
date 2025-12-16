# Semperis Directory Services Protector

| | |
|----------|-------|
| **Connector ID** | `SemperisDSP` |
| **Publisher** | SEMPERIS |
| **Tables Ingested** | [`SecurityEvent`](../tables-index.md#securityevent) |
| **Used in Solutions** | [Semperis Directory Services Protector](../solutions/semperis-directory-services-protector.md) |
| **Connector Definition Files** | [SemperisDSP-connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Data%20Connectors/SemperisDSP-connector.json) |

Semperis Directory Services Protector data connector allows for the export of its Windows event logs (i.e. Indicators of Exposure and Indicators of Compromise) to Microsoft Sentinel in real time.

It provides a data parser to manipulate the Windows event logs more easily. The different workbooks ease your Active Directory security monitoring and provide different ways to visualize the data. The analytic templates allow to automate responses regarding different events, exposures, or attacks.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**dsp_parser**](https://aka.ms/sentinel-SemperisDSP-parser) which is deployed with the Microsoft Sentinel Solution.

**2. **Configure Windows Security Events via AMA connector****

Collect Windows security events logs from your **Semperis DSP Management Server** .

**1. Install the Azure Monitor Agent (AMA)**

On your **Semperis DSP Management Server** install the AMA on the DSP machine that will act as the event log forwarder.
You can skip this step if you have already installed the Microsoft agent for Windows

**2. Create a Data Collection Rule (DCR)**

Start collecting logs from the **Semperis DSP Management Server** .

1. In the Azure portal, navigate to your **Log Analytics workspace**.
2. In the left pane, click on **Configuration** and then **Data connectors**.
3. Find and install the **the Windows Security Events via AMA** connector.
4. Click on **Open connector** and then on **Create data collection rule**.
5. Configure the DCR with the necessary details, such as the log sources and the destination workspace.
**Choose where to install the agent:**

**Install agent on Semperis DSP Management Server**

  Download the agent on the relevant machine and follow the instructions.
  - **Install/configure: InstallAgentOnNonAzure**

**3. **Configure Common Event Format via AMA connector****

Collect syslog messages send from your **Semperis DSP Management Server** .

**1. Install the Azure Monitor Agent (AMA)**

Install the AMA on the Linux machine that will act as the log forwarder. This machine will collect and forward CEF logs to Microsoft Sentinel.
You can skip this step if you have already installed the Microsoft agent for Linux

**2. Create a Data Collection Rule (DCR)**

Start collecting logs from the **Semperis DSP Management Server** .

1. In the Azure portal, navigate to your **Log Analytics workspace**.
2. In the left pane, click on **Configuration** and then **Data connectors**.
3. Find and install the **the Common Event Format via AMA** connector.
4. Click on **Open connector** and then on **Create data collection rule**.
5. Configure the DCR with the necessary details, such as the log sources and the destination workspace.
**Choose where to install the agent:**

**Install agent on Semperis DSP Management Server**

  Download the agent on the relevant machine and follow the instructions.
  - **Install/configure: InstallAgentOnNonAzure**

**3. Configure sending CEF logs on your Semperis DSP Management Server**

Configure your **Semperis DSP Management Server** to send CEF logs to the Linux machine where the AMA is installed. This involves setting the destination IP address and port for the CEF logs

> You should now be able to receive logs in the *Windows event log* table and *common log* table, log data can be parsed using the **dsp_parser()** function, used by all query samples, workbooks and analytic templates.

[← Back to Connectors Index](../connectors-index.md)
