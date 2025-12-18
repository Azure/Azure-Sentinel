# Perimeter 81

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Perimeter 81 |
| **Support Tier** | Partner |
| **Support Link** | [https://support.perimeter81.com/docs](https://support.perimeter81.com/docs) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Perimeter%2081](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Perimeter%2081) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Perimeter 81 Activity Logs](../connectors/perimeter81activitylogs.md)

**Publisher:** Perimeter 81

The Perimeter 81 Activity Logs connector allows you to easily connect your Perimeter 81 activity logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Please note the values below and follow the instructions <a href='https://support.perimeter81.com/hc/en-us/articles/360012680780'>here</a> to connect your Perimeter 81 activity logs with Microsoft Sentinel.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `Perimeter81_CL` |
| **Connector Definition Files** | [Perimeter81ActivityLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Perimeter%2081/Data%20Connectors/Perimeter81ActivityLogs.json) |

[→ View full connector details](../connectors/perimeter81activitylogs.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Perimeter81_CL` | [Perimeter 81 Activity Logs](../connectors/perimeter81activitylogs.md) |

[← Back to Solutions Index](../solutions-index.md)
