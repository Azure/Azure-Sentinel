# NXLog FIM

| | |
|----------|-------|
| **Connector ID** | `NXLogFIM` |
| **Publisher** | NXLog |
| **Tables Ingested** | [`NXLogFIM_CL`](../tables-index.md#nxlogfim_cl) |
| **Used in Solutions** | [NXLog FIM](../solutions/nxlog-fim.md) |
| **Connector Definition Files** | [NXLogFIM.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20FIM/Data%20Connectors/NXLogFIM.json) |

The [NXLog FIM](https://docs.nxlog.co/refman/current/im/fim.html) module allows for the scanning of files and directories, reporting detected additions, changes, renames and deletions on the designated paths through calculated checksums during successive scans. This REST API connector can efficiently export the configured FIM events to Microsoft Sentinel in real time.

[← Back to Connectors Index](../connectors-index.md)
