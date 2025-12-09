# [Deprecated] Proofpoint On Demand Email Security

| | |
|----------|-------|
| **Connector ID** | `ProofpointPOD` |
| **Publisher** | Proofpoint |
| **Tables Ingested** | [`ProofpointPODMessage_CL`](../tables-index.md#proofpointpodmessage_cl), [`ProofpointPOD_maillog_CL`](../tables-index.md#proofpointpod_maillog_cl), [`ProofpointPOD_message_CL`](../tables-index.md#proofpointpod_message_cl), [`maillog_CL`](../tables-index.md#maillog_cl) |
| **Used in Solutions** | [Proofpoint On demand(POD) Email Security](../solutions/proofpoint-on-demand(pod)-email-security.md) |
| **Connector Definition Files** | [ProofpointPOD_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Data%20Connectors/ProofpointPOD_API_FunctionApp.json) |

Proofpoint On Demand Email Security data connector provides the capability to get Proofpoint on Demand Email Protection data, allows users to check message traceability, monitoring into email activity, threats,and data exfiltration by attackers and malicious insiders. The connector provides ability to review events in your org on an accelerated basis, get event log files in hourly increments for recent activity.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
