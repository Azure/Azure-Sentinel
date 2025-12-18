# NXLog FIM

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | NXLog |
| **Support Tier** | Partner |
| **Support Link** | [https://nxlog.co/support-tickets/add/support-ticket](https://nxlog.co/support-tickets/add/support-ticket) |
| **Categories** | domains |
| **First Published** | 2022-08-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20FIM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20FIM) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [NXLog FIM](../connectors/nxlogfim.md)

**Publisher:** NXLog

The [NXLog FIM](https://docs.nxlog.co/refman/current/im/fim.html) module allows for the scanning of files and directories, reporting detected additions, changes, renames and deletions on the designated paths through calculated checksums during successive scans. This REST API connector can efficiently export the configured FIM events to Microsoft Sentinel in real time.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Follow the step-by-step instructions in the [Microsoft Sentinel](https://docs.nxlog.co/userguide/integrate/microsoft-azure-sentinel.html) integration chapter of the *NXLog User Guide* to configure this connector.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `NXLogFIM_CL` |
| **Connector Definition Files** | [NXLogFIM.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20FIM/Data%20Connectors/NXLogFIM.json) |

[→ View full connector details](../connectors/nxlogfim.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `NXLogFIM_CL` | [NXLog FIM](../connectors/nxlogfim.md) |

[← Back to Solutions Index](../solutions-index.md)
