# NXLog BSM macOS

| | |
|----------|-------|
| **Connector ID** | `NXLogBSMmacOS` |
| **Publisher** | NXLog |
| **Tables Ingested** | [`BSMmacOS_CL`](../tables-index.md#bsmmacos_cl) |
| **Used in Solutions** | [NXLog BSM macOS](../solutions/nxlog-bsm-macos.md) |
| **Connector Definition Files** | [NXLogBSMmacOS.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20BSM%20macOS/Data%20Connectors/NXLogBSMmacOS.json) |

The [NXLog BSM](https://docs.nxlog.co/refman/current/im/bsm.html) macOS data connector uses Sun's Basic Security Module (BSM) Auditing API to read events directly from the kernel for capturing audit events on the macOS platform. This REST API connector can efficiently export macOS audit events to Microsoft Sentinel in real-time.

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
