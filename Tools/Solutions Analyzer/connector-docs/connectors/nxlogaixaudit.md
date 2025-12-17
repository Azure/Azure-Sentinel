# NXLog AIX Audit

| | |
|----------|-------|
| **Connector ID** | `NXLogAixAudit` |
| **Publisher** | NXLog |
| **Tables Ingested** | [`AIX_Audit_CL`](../tables-index.md#aix_audit_cl) |
| **Used in Solutions** | [NXLogAixAudit](../solutions/nxlogaixaudit.md) |
| **Connector Definition Files** | [NXLogAixAudit.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogAixAudit/Data%20Connectors/NXLogAixAudit.json) |

The [NXLog AIX Audit](https://docs.nxlog.co/refman/current/im/aixaudit.html) data connector uses the AIX Audit subsystem to read events directly from the kernel for capturing audit events on the AIX platform. This REST API connector can efficiently export AIX Audit events to Microsoft Sentinel in real time.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**NXLog_parsed_AIX_Audit_view**](https://aka.ms/sentinel-nxlogaixaudit-parser) which is deployed with the Microsoft Sentinel Solution.

Follow the step-by-step instructions in the *NXLog User Guide* Integration Guide [Microsoft Sentinel](https://docs.nxlog.co/userguide/integrate/microsoft-azure-sentinel.html) to configure this connector.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
