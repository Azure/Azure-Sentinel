# CYFIRMA Cyber Intelligence

| | |
|----------|-------|
| **Connector ID** | `CyfirmaCyberIntelligenceDC` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CyfirmaCampaigns_CL`](../tables-index.md#cyfirmacampaigns_cl), [`CyfirmaIndicators_CL`](../tables-index.md#cyfirmaindicators_cl), [`CyfirmaMalware_CL`](../tables-index.md#cyfirmamalware_cl), [`CyfirmaThreatActors_CL`](../tables-index.md#cyfirmathreatactors_cl) |
| **Used in Solutions** | [Cyfirma Cyber Intelligence](../solutions/cyfirma-cyber-intelligence.md) |
| **Connector Definition Files** | [CyfirmaCyberIntel_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Data%20Connectors/CyfirmaCyberIntelligence_ccp/CyfirmaCyberIntel_DataConnectorDefinition.json) |

The CYFIRMA Cyber Intelligence data connector enables seamless log ingestion from the DeCYFIR API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the DeCYFIR Alerts API to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

[← Back to Connectors Index](../connectors-index.md)
