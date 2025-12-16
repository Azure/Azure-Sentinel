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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Zero Networks API Token**: **ZeroNetworksAPIToken** is required for REST API. See the API Guide and follow the instructions for obtaining credentials.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Zero Networks to Microsoft Sentinel**

Enable Zero Networks audit Logs.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

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
