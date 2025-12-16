# [Deprecated] PostgreSQL Events

| | |
|----------|-------|
| **Connector ID** | `PostgreSQL` |
| **Publisher** | PostgreSQL |
| **Tables Ingested** | [`PostgreSQL_CL`](../tables-index.md#postgresql_cl) |
| **Used in Solutions** | [PostgreSQL](../solutions/postgresql.md) |
| **Connector Definition Files** | [Connector_PostgreSQL.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PostgreSQL/Data%20Connectors/Connector_PostgreSQL.json) |

PostgreSQL data connector provides the capability to ingest [PostgreSQL](https://www.postgresql.org/) events into Microsoft Sentinel. Refer to [PostgreSQL documentation](https://www.postgresql.org/docs/current/index.html) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on PostgreSQL parser based on a Kusto Function to work as expected. This parser is installed along with solution installation.

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Tomcat Server where the logs are generated.

> Logs from PostgreSQL Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

**2. Configure PostgreSQL to write logs to files**

1. Edit postgresql.conf file to write logs to files:

>**log_destination** = 'stderr'

>**logging_collector** = on

Set the following parameters: **log_directory** and **log_filename**. Refer to the [PostgreSQL documentation for more details](https://www.postgresql.org/docs/current/runtime-config-logging.html)

**3. Configure the logs to be collected**

Configure the custom log directory to be collected
- **Open custom logs settings**

1. Select the link above to open your workspace advanced settings 
2. From the left pane, select **Settings**, select **Custom Logs** and click **+Add custom log**
3. Click **Browse** to upload a sample of a PostgreSQL log file. Then, click **Next >**
4. Select **Timestamp** as the record delimiter and click **Next >**
5. Select **Windows** or **Linux** and enter the path to PostgreSQL logs based on your configuration(e.g. for some Linux distros the default path is /var/log/postgresql/) 
6. After entering the path, click the '+' symbol to apply, then click **Next >** 
7. Add **PostgreSQL** as the custom log Name (the '_CL' suffix will be added automatically) and click **Done**.

**2. Validate connectivity**

It may take upwards of 20 minutes until your logs start to appear in Microsoft Sentinel.

[← Back to Connectors Index](../connectors-index.md)
