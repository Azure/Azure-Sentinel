# ProofPointTap

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Proofpoint, Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://proofpoint.my.site.com/community/s/](https://proofpoint.my.site.com/community/s/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Proofpoint TAP](../connectors/proofpointtap.md)

**Publisher:** Proofpoint

### [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md)

**Publisher:** Proofpoint

The [Proofpoint Targeted Attack Protection (TAP)](https://www.proofpoint.com/us/products/advanced-threat-protection/targeted-attack-protection) connector provides the capability to ingest Proofpoint TAP logs and events into Microsoft Sentinel. The connector provides visibility into Message and Click events in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `ProofPointTAPClicksBlockedV2_CL` |
| | `ProofPointTAPClicksPermittedV2_CL` |
| | `ProofPointTAPMessagesBlockedV2_CL` |
| | `ProofPointTAPMessagesDeliveredV2_CL` |
| **Connector Definition Files** | [ProofpointTAP_defination.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap/Data%20Connectors/ProofpointTAP_CCP/ProofpointTAP_defination.json) |

[→ View full connector details](../connectors/proofpointtapv2.md)

## Tables Reference

This solution ingests data into **8 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ProofPointTAPClicksBlockedV2_CL` | [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md) |
| `ProofPointTAPClicksBlocked_CL` | [[Deprecated] Proofpoint TAP](../connectors/proofpointtap.md) |
| `ProofPointTAPClicksPermittedV2_CL` | [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md) |
| `ProofPointTAPClicksPermitted_CL` | [[Deprecated] Proofpoint TAP](../connectors/proofpointtap.md) |
| `ProofPointTAPMessagesBlockedV2_CL` | [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md) |
| `ProofPointTAPMessagesBlocked_CL` | [[Deprecated] Proofpoint TAP](../connectors/proofpointtap.md) |
| `ProofPointTAPMessagesDeliveredV2_CL` | [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md) |
| `ProofPointTAPMessagesDelivered_CL` | [[Deprecated] Proofpoint TAP](../connectors/proofpointtap.md) |

[← Back to Solutions Index](../solutions-index.md)
