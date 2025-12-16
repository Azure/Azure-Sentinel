# NXLogDnsLogs

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | NXLog |
| **Support Tier** | Partner |
| **Support Link** | [https://nxlog.co/support-tickets/add/support-ticket](https://nxlog.co/support-tickets/add/support-ticket) |
| **Categories** | domains |
| **First Published** | 2022-05-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogDnsLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogDnsLogs) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [NXLog DNS Logs](../connectors/nxlogdnslogs.md)

**Publisher:** NXLog

The NXLog DNS Logs data connector uses Event Tracing for Windows ([ETW](https://docs.microsoft.com/windows/apps/trace-processing/overview)) for collecting both Audit and Analytical DNS Server events. The [NXLog *im_etw* module](https://docs.nxlog.co/refman/current/im/etw.html) reads event tracing data directly for maximum efficiency, without the need to capture the event trace into an .etl file. This REST API connector can forward DNS Server events to Microsoft Sentinel in real time.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on parsers based on Kusto functions deployed with the Microsoft Sentinel Solution to work as expected. The [**ASimDnsMicrosoftNXLog **](https://aka.ms/sentinel-nxlogdnslogs-parser) is designed to leverage Microsoft Sentinel's built-in DNS-related analytics capabilities.

Follow the step-by-step instructions in the *NXLog User Guide* Integration Topic [Microsoft Sentinel](https://docs.nxlog.co/userguide/integrate/microsoft-azure-sentinel.html) to configure this connector.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `NXLog_DNS_Server_CL` |
| **Connector Definition Files** | [NXLogDnsLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogDnsLogs/Data%20Connectors/NXLogDnsLogs.json) |

[→ View full connector details](../connectors/nxlogdnslogs.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `NXLog_DNS_Server_CL` | [NXLog DNS Logs](../connectors/nxlogdnslogs.md) |

[← Back to Solutions Index](../solutions-index.md)
