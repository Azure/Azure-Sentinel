# NXLog LinuxAudit

| | |
|----------|-------|
| **Connector ID** | `NXLogLinuxAudit` |
| **Publisher** | NXLog |
| **Tables Ingested** | [`LinuxAudit_CL`](../tables-index.md#linuxaudit_cl) |
| **Used in Solutions** | [NXLog LinuxAudit](../solutions/nxlog-linuxaudit.md) |
| **Connector Definition Files** | [NXLogLinuxAudit.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20LinuxAudit/Data%20Connectors/NXLogLinuxAudit.json) |

The [NXLog LinuxAudit](https://docs.nxlog.co/refman/current/im/linuxaudit.html) data connector supports custom audit rules and collects logs without auditd or any other user-space software. IP addresses and group/user IDs are resolved to their respective names making [Linux audit](https://docs.nxlog.co/userguide/integrate/linux-audit.html) logs more intelligible to security analysts. This REST API connector can efficiently export Linux security events to Microsoft Sentinel in real-time.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Follow the step-by-step instructions in the *NXLog User Guide* Integration Topic [Microsoft Sentinel](https://docs.nxlog.co/userguide/integrate/microsoft-azure-sentinel.html) to configure this connector.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
