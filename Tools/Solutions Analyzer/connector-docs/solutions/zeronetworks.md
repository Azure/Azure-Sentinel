# ZeroNetworks

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Zero Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://zeronetworks.com](https://zeronetworks.com) |
| **Categories** | domains |
| **First Published** | 2022-06-06 |
| **Last Updated** | 2025-09-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Zero Networks Segment Audit](../connectors/zeronetworkssegmentauditnativepoller.md)

**Publisher:** Zero Networks

The [Zero Networks Segment](https://zeronetworks.com/) Audit data connector provides the capability to ingest Zero Networks Audit events into Microsoft Sentinel through the REST API. This data connector uses Microsoft Sentinel native polling capability.

| | |
|--------------------------|---|
| **Tables Ingested** | `ZNSegmentAuditNativePoller_CL` |
| **Connector Definition Files** | [azuredeploy_ZeroNetworks_Segment_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Data%20Connectors/SegmentNativePollerConnector/azuredeploy_ZeroNetworks_Segment_native_poller_connector.json) |

[→ View full connector details](../connectors/zeronetworkssegmentauditnativepoller.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ZNSegmentAuditNativePoller_CL` | [Zero Networks Segment Audit](../connectors/zeronetworkssegmentauditnativepoller.md) |

[← Back to Solutions Index](../solutions-index.md)
