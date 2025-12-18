# Talon Insights

| | |
|----------|-------|
| **Connector ID** | `TalonLogs` |
| **Publisher** | Talon Security |
| **Tables Ingested** | [`Talon_CL`](../tables-index.md#talon_cl) |
| **Used in Solutions** | [Talon](../solutions/talon.md) |
| **Connector Definition Files** | [TalonLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Talon/Data%20Connectors/TalonLogs.json) |

The Talon Security Logs connector allows you to easily connect your Talon events and audit logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Please note the values below and follow the instructions <a href='https://docs.console.talon-sec.com/en/articles/254-microsoft-sentinel-integration'>here</a> to connect your Talon Security events and audit logs with Microsoft Sentinel.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
