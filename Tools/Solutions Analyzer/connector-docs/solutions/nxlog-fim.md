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
