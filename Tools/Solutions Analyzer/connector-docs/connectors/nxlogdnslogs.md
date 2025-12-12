# NXLog DNS Logs

| | |
|----------|-------|
| **Connector ID** | `NXLogDNSLogs` |
| **Publisher** | NXLog |
| **Tables Ingested** | [`NXLog_DNS_Server_CL`](../tables-index.md#nxlog_dns_server_cl) |
| **Used in Solutions** | [NXLogDnsLogs](../solutions/nxlogdnslogs.md) |
| **Connector Definition Files** | [NXLogDnsLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogDnsLogs/Data%20Connectors/NXLogDnsLogs.json) |

The NXLog DNS Logs data connector uses Event Tracing for Windows ([ETW](https://docs.microsoft.com/windows/apps/trace-processing/overview)) for collecting both Audit and Analytical DNS Server events. The [NXLog *im_etw* module](https://docs.nxlog.co/refman/current/im/etw.html) reads event tracing data directly for maximum efficiency, without the need to capture the event trace into an .etl file. This REST API connector can forward DNS Server events to Microsoft Sentinel in real time.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on parsers based on Kusto functions deployed with the Microsoft Sentinel Solution to work as expected. The [**ASimDnsMicrosoftNXLog **](https://aka.ms/sentinel-nxlogdnslogs-parser) is designed to leverage Microsoft Sentinel's built-in DNS-related analytics capabilities.

Follow the step-by-step instructions in the *NXLog User Guide* Integration Topic [Microsoft Sentinel](https://docs.nxlog.co/userguide/integrate/microsoft-azure-sentinel.html) to configure this connector.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
