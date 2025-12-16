# [Deprecated] Digital Guardian Data Loss Prevention

| | |
|----------|-------|
| **Connector ID** | `DigitalGuardianDLP` |
| **Publisher** | Digital Guardian |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Digital Guardian Data Loss Prevention](../solutions/digital-guardian-data-loss-prevention.md) |
| **Connector Definition Files** | [Connector_DigitalGuardian_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Data%20Connectors/Connector_DigitalGuardian_Syslog.json) |

[Digital Guardian Data Loss Prevention (DLP)](https://digitalguardian.com/platform-overview) data connector provides the capability to ingest Digital Guardian DLP logs into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**DigitalGuardianDLPEvent**](https://aka.ms/sentinel-DigitalGuardianDLP-parser) which is deployed with the Microsoft Sentinel Solution.

**1. Configure Digital Guardian to forward logs via Syslog to remote server where you will install the agent.**

Follow these steps to configure Digital Guardian to forward logs via Syslog:

1.1. Log in to the Digital Guardian Management Console.

1.2. Select **Workspace** > **Data Export** > **Create Export**.

1.3. From the **Data Sources** list, select **Alerts** or **Events** as the data source.

1.4. From the **Export type** list, select **Syslog**.

1.5. From the **Type list**, select **UDP** or **TCP** as the transport protocol.

1.6. In the **Server** field, type the IP address of your Remote Syslog server.

1.7. In the **Port** field, type 514 (or other port if your Syslog server was configured to use non-default port).

1.8. From the **Severity Level** list, select a severity level.

1.9. Select the **Is Active** check box.

1.9. Click **Next**.

1.10. From the list of available fields, add Alert or Event fields for your data export.

1.11. Select a Criteria for the fields in your data export and click **Next**.

1.12. Select a group for the criteria and click **Next**.

1.13. Click **Test Query**.

1.14. Click **Next**.

1.15. Save the data export.

**2. Install and onboard the agent for Linux or Windows**

Install the agent on the Server to which the logs will be forwarded.

> Logs on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

**3. Check logs in Microsoft Sentinel**

Open Log Analytics to check if the logs are received using the Syslog schema.

>**NOTE:** It may take up to 15 minutes before new logs will appear in Syslog table.

[← Back to Connectors Index](../connectors-index.md)
