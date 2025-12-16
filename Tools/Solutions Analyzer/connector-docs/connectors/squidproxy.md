# [Deprecated] Squid Proxy

| | |
|----------|-------|
| **Connector ID** | `SquidProxy` |
| **Publisher** | Squid |
| **Tables Ingested** | [`SquidProxy_CL`](../tables-index.md#squidproxy_cl) |
| **Used in Solutions** | [SquidProxy](../solutions/squidproxy.md) |
| **Connector Definition Files** | [Connector_CustomLog_SquidProxy.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SquidProxy/Data%20Connectors/Connector_CustomLog_SquidProxy.json) |

The [Squid Proxy](http://www.squid-cache.org/) connector allows you to easily connect your Squid Proxy logs with Microsoft Sentinel. This gives you more insight into your organization's network proxy traffic and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias Squid Proxy and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SquidProxy/Parsers/SquidProxy.txt), on the second line of the query, enter the hostname(s) of your SquidProxy device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Squid Proxy server where the logs are generated.

> Logs from Squid Proxy deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

Configure the custom log directory to be collected
- **Open custom logs settings**

1. Select the link above to open your workspace advanced settings 
2. From the left pane, select **Data**, select **Custom Logs** and click **Add+**
3. Click **Browse** to upload a sample of a Squid Proxy log file(e.g. access.log or cache.log). Then, click **Next >**
4. Select **New line** as the record delimiter and click **Next >**
5. Select **Windows** or **Linux** and enter the path to Squid Proxy logs. Default paths are: 
 - **Windows** directory: `C:\Squid\var\log\squid\*.log`
 - **Linux** Directory:  `/var/log/squid/*.log` 
6. After entering the path, click the '+' symbol to apply, then click **Next >** 
7. Add **SquidProxy_CL** as the custom log Name and click **Done**

[← Back to Connectors Index](../connectors-index.md)
