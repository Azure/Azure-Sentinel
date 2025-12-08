# Pathlock Inc.: Threat Detection and Response for SAP

| | |
|----------|-------|
| **Connector ID** | `Pathlock_TDnR` |
| **Publisher** | Pathlock Inc. |
| **Tables Ingested** | [`ABAPAuditLog`](../tables-index.md#abapauditlog), [`Pathlock_TDnR_CL`](../tables-index.md#pathlock_tdnr_cl) |
| **Used in Solutions** | [Pathlock_TDnR](../solutions/pathlock-tdnr.md) |
| **Connector Definition Files** | [Pathlock_TDnR_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pathlock_TDnR/Data%20Connectors/Pathlock_TDnR_PUSH_CCP/Pathlock_TDnR_connectorDefinition.json) |

The [Pathlock Threat Detection and Response (TD&R)](https://pathlock.com/products/cybersecurity-application-controls/) integration with **Microsoft Sentinel Solution for SAP** delivers unified, real-time visibility into SAP security events, enabling organizations to detect and act on threats across all SAP landscapes. This out-of-the-box integration allows Security Operations Centers (SOCs) to correlate SAP-specific alerts with enterprise-wide telemetry, creating actionable intelligence that connects IT security with business processes.



Pathlock’s connector is purpose-built for SAP and forwards only **security-relevant events by default**, minimizing data volume and noise while maintaining the flexibility to forward all log sources when needed. Each event is enriched with **business process context**, allowing Microsoft Sentinel Solution for SAP analytics to distinguish operational patterns from real threats and to prioritize what truly matters.



This precision-driven approach helps security teams drastically reduce false positives, focus investigations, and accelerate **mean time to detect (MTTD)** and **mean time to respond (MTTR)**. Pathlock’s library consists of more than 1,500 SAP-specific detection signatures across 70+ log sources, the solution uncovers complex attack behaviors, configuration weaknesses, and access anomalies.



By combining business-context intelligence with advanced analytics, Pathlock enables enterprises to strengthen detection accuracy, streamline response actions, and maintain continuous control across their SAP environments—without adding complexity or redundant monitoring layers.

[← Back to Connectors Index](../connectors-index.md)
