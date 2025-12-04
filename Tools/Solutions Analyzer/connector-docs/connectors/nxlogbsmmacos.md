# NXLog BSM macOS

| | |
|----------|-------|
| **Connector ID** | `NXLogBSMmacOS` |
| **Publisher** | NXLog |
| **Tables Ingested** | [`BSMmacOS_CL`](../tables-index.md#bsmmacos_cl) |
| **Used in Solutions** | [NXLog BSM macOS](../solutions/nxlog-bsm-macos.md) |
| **Connector Definition Files** | [NXLogBSMmacOS.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLog%20BSM%20macOS/Data%20Connectors/NXLogBSMmacOS.json) |

The [NXLog BSM](https://docs.nxlog.co/refman/current/im/bsm.html) macOS data connector uses Sun's Basic Security Module (BSM) Auditing API to read events directly from the kernel for capturing audit events on the macOS platform. This REST API connector can efficiently export macOS audit events to Microsoft Sentinel in real-time.

[← Back to Connectors Index](../connectors-index.md)
