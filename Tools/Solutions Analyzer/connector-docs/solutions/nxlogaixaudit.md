# NXLogAixAudit

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | NXLog |
| **Support Tier** | Partner |
| **Support Link** | [https://nxlog.co/support-tickets/add/support-ticket](https://nxlog.co/support-tickets/add/support-ticket) |
| **Categories** | domains |
| **First Published** | 2022-05-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogAixAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogAixAudit) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [NXLog AIX Audit](../connectors/nxlogaixaudit.md)

**Publisher:** NXLog

The [NXLog AIX Audit](https://docs.nxlog.co/refman/current/im/aixaudit.html) data connector uses the AIX Audit subsystem to read events directly from the kernel for capturing audit events on the AIX platform. This REST API connector can efficiently export AIX Audit events to Microsoft Sentinel in real time.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**NXLog_parsed_AIX_Audit_view**](https://aka.ms/sentinel-nxlogaixaudit-parser) which is deployed with the Microsoft Sentinel Solution.

Follow the step-by-step instructions in the *NXLog User Guide* Integration Guide [Microsoft Sentinel](https://docs.nxlog.co/userguide/integrate/microsoft-azure-sentinel.html) to configure this connector.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `AIX_Audit_CL` |
| **Connector Definition Files** | [NXLogAixAudit.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogAixAudit/Data%20Connectors/NXLogAixAudit.json) |

[→ View full connector details](../connectors/nxlogaixaudit.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AIX_Audit_CL` | [NXLog AIX Audit](../connectors/nxlogaixaudit.md) |

[← Back to Solutions Index](../solutions-index.md)
