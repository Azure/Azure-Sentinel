# NXLog AIX Audit

| | |
|----------|-------|
| **Connector ID** | `NXLogAixAudit` |
| **Publisher** | NXLog |
| **Tables Ingested** | [`AIX_Audit_CL`](../tables-index.md#aix_audit_cl) |
| **Used in Solutions** | [NXLogAixAudit](../solutions/nxlogaixaudit.md) |
| **Connector Definition Files** | [NXLogAixAudit.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogAixAudit/Data%20Connectors/NXLogAixAudit.json) |

The [NXLog AIX Audit](https://docs.nxlog.co/refman/current/im/aixaudit.html) data connector uses the AIX Audit subsystem to read events directly from the kernel for capturing audit events on the AIX platform. This REST API connector can efficiently export AIX Audit events to Microsoft Sentinel in real time.

[← Back to Connectors Index](../connectors-index.md)
