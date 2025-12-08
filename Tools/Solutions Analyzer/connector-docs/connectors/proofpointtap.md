# [Deprecated] Proofpoint TAP

| | |
|----------|-------|
| **Connector ID** | `ProofpointTAP` |
| **Publisher** | Proofpoint |
| **Tables Ingested** | [`ProofPointTAPClicksBlocked_CL`](../tables-index.md#proofpointtapclicksblocked_cl), [`ProofPointTAPClicksPermitted_CL`](../tables-index.md#proofpointtapclickspermitted_cl), [`ProofPointTAPMessagesBlocked_CL`](../tables-index.md#proofpointtapmessagesblocked_cl), [`ProofPointTAPMessagesDelivered_CL`](../tables-index.md#proofpointtapmessagesdelivered_cl) |
| **Used in Solutions** | [ProofPointTap](../solutions/proofpointtap.md) |
| **Connector Definition Files** | [ProofpointTAP_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap/Data%20Connectors/ProofpointTAP_API_FunctionApp.json) |

The [Proofpoint Targeted Attack Protection (TAP)](https://www.proofpoint.com/us/products/advanced-threat-protection/targeted-attack-protection) connector provides the capability to ingest Proofpoint TAP logs and events into Microsoft Sentinel. The connector provides visibility into Message and Click events in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
