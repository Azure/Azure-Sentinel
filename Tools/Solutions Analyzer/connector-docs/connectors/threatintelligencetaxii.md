# Threat intelligence - TAXII

| | |
|----------|-------|
| **Connector ID** | `ThreatIntelligenceTaxii` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ThreatIntelIndicators`](../tables-index.md#threatintelindicators), [`ThreatIntelObjects`](../tables-index.md#threatintelobjects), [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [Threat Intelligence](../solutions/threat-intelligence.md), [Threat Intelligence (NEW)](../solutions/threat-intelligence-(new).md) |
| **Connector Definition Files** | [template_ThreatIntelligenceTaxii.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Data%20Connectors/template_ThreatIntelligenceTaxii.json) |

Microsoft Sentinel integrates with TAXII 2.0 and 2.1 data sources to enable monitoring, alerting, and hunting using your threat intelligence. Use this connector to send the supported STIX object types from TAXII servers to Microsoft Sentinel. Threat indicators can include IP addresses, domains, URLs, and file hashes. For more information, see the [Microsoft Sentinel documentation >](https://go.microsoft.com/fwlink/p/?linkid=2224105&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[← Back to Connectors Index](../connectors-index.md)
