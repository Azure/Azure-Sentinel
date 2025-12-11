# [Deprecated] JBoss Enterprise Application Platform

| | |
|----------|-------|
| **Connector ID** | `JBossEAP` |
| **Publisher** | Red Hat |
| **Tables Ingested** | [`JBossLogs_CL`](../tables-index.md#jbosslogs_cl) |
| **Used in Solutions** | [JBoss](../solutions/jboss.md) |
| **Connector Definition Files** | [Connector_JBoss.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JBoss/Data%20Connectors/Connector_JBoss.json) |

The JBoss Enterprise Application Platform data connector provides the capability to ingest [JBoss](https://www.redhat.com/en/technologies/jboss-middleware/application-platform) events into Microsoft Sentinel. Refer to [Red Hat documentation](https://access.redhat.com/documentation/en-us/red_hat_jboss_enterprise_application_platform/7.0/html/configuration_guide/logging_with_jboss_eap) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**JBossEvent**](https://aka.ms/sentinel-jbosseap-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:** This data connector has been developed using JBoss Enterprise Application Platform 7.4.0.

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the JBoss server where the logs are generated.

>  Logs from JBoss Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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
2. Click **+Add custom**
3. Click **Browse** to upload a sample of a JBoss log file (e.g. server.log). Then, click **Next >**
4. Select **Timestamp** as the record delimiter and select Timestamp format **YYYY-MM-DD HH:MM:SS** from the dropdown list then click **Next >**
5. Select **Windows** or **Linux** and enter the path to JBoss logs based on your configuration. Example:
 - **Linux** Directory:

>Standalone server: EAP_HOME/standalone/log/server.log

>Managed domain: EAP_HOME/domain/servers/SERVER_NAME/log/server.log

6. After entering the path, click the '+' symbol to apply, then click **Next >** 
7. Add **JBossLogs** as the custom log Name and click **Done**

**3. Check logs in Microsoft Sentinel**

Open Log Analytics to check if the logs are received using the JBossLogs_CL Custom log table.

>**NOTE:** It may take up to 30 minutes before new logs will appear in JBossLogs_CL table.

[← Back to Connectors Index](../connectors-index.md)
