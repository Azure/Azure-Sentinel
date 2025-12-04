# Proofpoint On demand(POD) Email Security

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Proofpoint, Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://proofpoint.my.site.com/community/s/](https://proofpoint.my.site.com/community/s/) |
| **Categories** | domains |
| **First Published** | 2021-03-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md)

**Publisher:** Proofpoint

### [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md)

**Publisher:** Proofpoint

Proofpoint On Demand Email Security data connector provides the capability to get Proofpoint on Demand Email Protection data, allows users to check message traceability, monitoring into email activity, threats,and data exfiltration by attackers and malicious insiders. The connector provides ability to review events in your org on an accelerated basis, get event log files in hourly increments for recent activity.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| | |
|--------------------------|---|
| **Tables Ingested** | `ProofpointPODMessage_CL` |
| | `ProofpointPOD_maillog_CL` |
| | `ProofpointPOD_message_CL` |
| | `maillog_CL` |
| **Connector Definition Files** | [ProofpointPOD_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Data%20Connectors/ProofpointPOD_API_FunctionApp.json) |

[→ View full connector details](../connectors/proofpointpod.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ProofpointPODMailLog_CL` | [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md) |
| `ProofpointPODMessage_CL` | [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md), [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |
| `ProofpointPOD_maillog_CL` | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |
| `ProofpointPOD_message_CL` | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |
| `maillog_CL` | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |

[← Back to Solutions Index](../solutions-index.md)
