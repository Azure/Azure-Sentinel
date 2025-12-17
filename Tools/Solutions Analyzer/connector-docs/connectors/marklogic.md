# [Deprecated] MarkLogic Audit

| | |
|----------|-------|
| **Connector ID** | `MarkLogic` |
| **Publisher** | MarkLogic |
| **Used in Solutions** | [MarkLogicAudit](../solutions/marklogicaudit.md) |
| **Connector Definition Files** | [Connector_MarkLogicAudit.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MarkLogicAudit/Data%20Connectors/Connector_MarkLogicAudit.json) |

MarkLogic data connector provides the capability to ingest [MarkLogicAudit](https://www.marklogic.com/) logs into Microsoft Sentinel. Refer to [MarkLogic documentation](https://docs.marklogic.com/guide/getting-started) for more information.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`MarkLogicAudit_CL`](../tables/marklogicaudit-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias MarkLogicAudit and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MarkLogicAudit/Parsers/MarkLogicAudit.txt) on the second line of the query, enter the hostname(s) of your MarkLogicAudit device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Tomcat Server where the logs are generated.

> Logs from MarkLogic Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

**2. Configure MarkLogicAudit to enable auditing**

Perform the following steps to enable auditing for a group:

>Access the Admin Interface with a browser;

>Open the Audit Configuration screen (Groups > group_name > Auditing);

>Select True for the Audit Enabled radio button;

>Configure any audit events and/or audit restrictions you want;

>Click OK.

 Refer to the [MarkLogic documentation for more details](https://docs.marklogic.com/guide/admin/auditing)

**3. Configure the logs to be collected**

Configure the custom log directory to be collected
- **Open custom logs settings**

1. Select the link above to open your workspace advanced settings 
2. From the left pane, select **Settings**, select **Custom Logs** and click **+Add custom log**
3. Click **Browse** to upload a sample of a MarkLogicAudit log file. Then, click **Next >**
4. Select **Timestamp** as the record delimiter and click **Next >**
5. Select **Windows** or **Linux** and enter the path to MarkLogicAudit logs based on your configuration 
6. After entering the path, click the '+' symbol to apply, then click **Next >** 
7. Add **MarkLogicAudit** as the custom log Name (the '_CL' suffix will be added automatically) and click **Done**.

**3. Validate connectivity**

It may take upwards of 20 minutes until your logs start to appear in Microsoft Sentinel.

[← Back to Connectors Index](../connectors-index.md)
