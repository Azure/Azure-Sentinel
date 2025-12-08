# NXLog BSM macOS

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | NXLog |
| **Support Tier** | Partner |
| **Support Link** | [https://nxlog.co/support-tickets/add/support-ticket](https://nxlog.co/support-tickets/add/support-ticket) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20BSM%20macOS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20BSM%20macOS) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [NXLog BSM macOS](../connectors/nxlogbsmmacos.md)

**Publisher:** NXLog

The [NXLog BSM](https://docs.nxlog.co/refman/current/im/bsm.html) macOS data connector uses Sun's Basic Security Module (BSM) Auditing API to read events directly from the kernel for capturing audit events on the macOS platform. This REST API connector can efficiently export macOS audit events to Microsoft Sentinel in real-time.

| | |
|--------------------------|---|
| **Tables Ingested** | `BSMmacOS_CL` |
| **Connector Definition Files** | [NXLogBSMmacOS.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20BSM%20macOS/Data%20Connectors/NXLogBSMmacOS.json) |

[→ View full connector details](../connectors/nxlogbsmmacos.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BSMmacOS_CL` | [NXLog BSM macOS](../connectors/nxlogbsmmacos.md) |

[← Back to Solutions Index](../solutions-index.md)
