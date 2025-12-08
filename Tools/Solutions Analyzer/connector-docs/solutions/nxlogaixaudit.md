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
