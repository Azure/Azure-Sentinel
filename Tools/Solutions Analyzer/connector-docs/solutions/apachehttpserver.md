# ApacheHTTPServer

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Apache HTTP Server](../connectors/apachehttpserver.md)

**Publisher:** Apache

The Apache HTTP Server data connector provides the capability to ingest [Apache HTTP Server](http://httpd.apache.org/) events into Microsoft Sentinel. Refer to [Apache Logs documentation](https://httpd.apache.org/docs/2.4/logs.html) for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias ApacheHTTPServer and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Parsers/ApacheHTTPServer.txt). The function usually takes 10-15 minutes to activate after solution installation/update.

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Apache HTTP Server where the logs are generated.

> Logs from Apache HTTP Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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
3. Click **Browse** to upload a sample of a Apache HTTP Server log file (e.g. access.log or error.log). Then, click **Next >**
4. Select **New line** as the record delimiter and click **Next >**
5. Select **Windows** or **Linux** and enter the path to Apache HTTP logs based on your configuration. Example: 
 - **Windows** directory: `C:\Server\bin\Apache24\logs\*.log`
 - **Linux** Directory:  `/var/log/httpd/*.log` 
6. After entering the path, click the '+' symbol to apply, then click **Next >** 
7. Add **ApacheHTTPServer_CL** as the custom log Name and click **Done**

| | |
|--------------------------|---|
| **Tables Ingested** | `ApacheHTTPServer_CL` |
| **Connector Definition Files** | [Connector_ApacheHTTPServer_agent.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Data%20Connectors/Connector_ApacheHTTPServer_agent.json) |

[→ View full connector details](../connectors/apachehttpserver.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ApacheHTTPServer_CL` | [[Deprecated] Apache HTTP Server](../connectors/apachehttpserver.md) |

[← Back to Solutions Index](../solutions-index.md)
