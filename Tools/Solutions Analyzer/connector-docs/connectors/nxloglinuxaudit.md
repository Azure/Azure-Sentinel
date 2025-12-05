# NXLog LinuxAudit

| | |
|----------|-------|
| **Connector ID** | `NXLogLinuxAudit` |
| **Publisher** | NXLog |
| **Tables Ingested** | [`LinuxAudit_CL`](../tables-index.md#linuxaudit_cl) |
| **Used in Solutions** | [NXLog LinuxAudit](../solutions/nxlog-linuxaudit.md) |
| **Connector Definition Files** | [NXLogLinuxAudit.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20LinuxAudit/Data%20Connectors/NXLogLinuxAudit.json) |

The [NXLog LinuxAudit](https://docs.nxlog.co/refman/current/im/linuxaudit.html) data connector supports custom audit rules and collects logs without auditd or any other user-space software. IP addresses and group/user IDs are resolved to their respective names making [Linux audit](https://docs.nxlog.co/userguide/integrate/linux-audit.html) logs more intelligible to security analysts. This REST API connector can efficiently export Linux security events to Microsoft Sentinel in real-time.

[← Back to Connectors Index](../connectors-index.md)
