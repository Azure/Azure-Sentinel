# Talon

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Talon Security |
| **Support Tier** | Partner |
| **Support Link** | [https://docs.console.talon-sec.com/](https://docs.console.talon-sec.com/) |
| **Categories** | domains |
| **First Published** | 2023-01-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Talon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Talon) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Talon Insights](../connectors/talonlogs.md)

**Publisher:** Talon Security

The Talon Security Logs connector allows you to easily connect your Talon events and audit logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Please note the values below and follow the instructions <a href='https://docs.console.talon-sec.com/en/articles/254-microsoft-sentinel-integration'>here</a> to connect your Talon Security events and audit logs with Microsoft Sentinel.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `Talon_CL` |
| **Connector Definition Files** | [TalonLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Talon/Data%20Connectors/TalonLogs.json) |

[→ View full connector details](../connectors/talonlogs.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Talon_CL` | [Talon Insights](../connectors/talonlogs.md) |

[← Back to Solutions Index](../solutions-index.md)
