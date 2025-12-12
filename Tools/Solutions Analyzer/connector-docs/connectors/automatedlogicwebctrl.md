# Automated Logic WebCTRL 

| | |
|----------|-------|
| **Connector ID** | `AutomatedLogicWebCTRL` |
| **Publisher** | AutomatedLogic |
| **Tables Ingested** | [`Event`](../tables-index.md#event) |
| **Used in Solutions** | [ALC-WebCTRL](../solutions/alc-webctrl.md) |
| **Connector Definition Files** | [Connector_WindowsEvents_WebCTRL.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ALC-WebCTRL/Data%20Connectors/Connector_WindowsEvents_WebCTRL.json) |

You can stream the audit logs from the WebCTRL SQL server hosted on Windows machines connected to your Microsoft Sentinel. This connection enables you to view dashboards, create custom alerts and improve investigation. This gives insights into your Industrial Control Systems that are monitored or controlled by the WebCTRL BAS application.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Install and onboard the Microsoft agent for Windows.**

Learn about [agent setup](https://docs.microsoft.com/services-hub/health/mma-setup) and [windows events onboarding](https://docs.microsoft.com/azure/azure-monitor/agents/data-sources-windows-events). 

 You can skip this step if you have already installed the Microsoft agent for Windows

**2. Configure Windows task to read the audit data and write it to windows events**

Install and configure the Windows Scheduled Task to read the audit logs in SQL and write them as Windows Events. These Windows Events will be collected by the agent and forward to Microsoft Sentinel.

> Notice that the data from all machines will be stored in the selected workspace
2.1 Copy the [setup files](https://aka.ms/sentinel-automatedlogicwebctrl-tasksetup) to a location on the server.

  2.2 Update the [ALC-WebCTRL-AuditPull.ps1](https://aka.ms/sentinel-automatedlogicwebctrl-auditpull) (copied in above step) script parameters like the target database name and windows event id's. Refer comments in the script for more details.

  2.3 Update the windows task settings in the [ALC-WebCTRL-AuditPullTaskConfig.xml](https://aka.ms/sentinel-automatedlogicwebctrl-auditpulltaskconfig) file that was copied in above step as per requirement. Refer comments in the file for more details.

  2.4 Install windows tasks using the updated configs copied in the above steps
  - **Run the following command in powershell from the directory where the setup files are copied in step 2.1**: `schtasks.exe /create /XML "ALC-WebCTRL-AuditPullTaskConfig.xml" /tn "ALC-WebCTRL-AuditPull"`
**3. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the Event schema.

>It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, validate below steps for any run time issues:

> 1. Make sure that the scheduled task is created and is in running state in the Windows Task Scheduler.

>2. Check for task execution errors in the history tab in Windows Task Scheduler for the newly created task in step 2.4

>3. Make sure that the SQL Audit table consists new records while the scheduled windows task runs.

[← Back to Connectors Index](../connectors-index.md)
