# ProofPointTap

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Proofpoint, Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://proofpoint.my.site.com/community/s/](https://proofpoint.my.site.com/community/s/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] Proofpoint TAP

**Publisher:** Proofpoint

The [Proofpoint Targeted Attack Protection (TAP)](https://www.proofpoint.com/us/products/advanced-threat-protection/targeted-attack-protection) connector provides the capability to ingest Proofpoint TAP logs and events into Microsoft Sentinel. The connector provides visibility into Message and Click events in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

**Tables Ingested:**

- `ProofPointTAPClicksBlocked_CL`
- `ProofPointTAPClicksPermitted_CL`
- `ProofPointTAPMessagesBlocked_CL`
- `ProofPointTAPMessagesDelivered_CL`

**Connector Definition Files:**

- [ProofpointTAP_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap/Data%20Connectors/ProofpointTAP_API_FunctionApp.json)

### Proofpoint TAP (via Codeless Connector Platform)

**Publisher:** Proofpoint

The [Proofpoint Targeted Attack Protection (TAP)](https://www.proofpoint.com/us/products/advanced-threat-protection/targeted-attack-protection) connector provides the capability to ingest Proofpoint TAP logs and events into Microsoft Sentinel. The connector provides visibility into Message and Click events in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

**Tables Ingested:**

- `ProofPointTAPClicksBlockedV2_CL`
- `ProofPointTAPClicksPermittedV2_CL`
- `ProofPointTAPMessagesBlockedV2_CL`
- `ProofPointTAPMessagesDeliveredV2_CL`

**Connector Definition Files:**

- [ProofpointTAP_defination.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap/Data%20Connectors/ProofpointTAP_CCP/ProofpointTAP_defination.json)

## Tables Reference

This solution ingests data into **8 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ProofPointTAPClicksBlockedV2_CL` | Proofpoint TAP (via Codeless Connector Platform) |
| `ProofPointTAPClicksBlocked_CL` | [Deprecated] Proofpoint TAP |
| `ProofPointTAPClicksPermittedV2_CL` | Proofpoint TAP (via Codeless Connector Platform) |
| `ProofPointTAPClicksPermitted_CL` | [Deprecated] Proofpoint TAP |
| `ProofPointTAPMessagesBlockedV2_CL` | Proofpoint TAP (via Codeless Connector Platform) |
| `ProofPointTAPMessagesBlocked_CL` | [Deprecated] Proofpoint TAP |
| `ProofPointTAPMessagesDeliveredV2_CL` | Proofpoint TAP (via Codeless Connector Platform) |
| `ProofPointTAPMessagesDelivered_CL` | [Deprecated] Proofpoint TAP |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n