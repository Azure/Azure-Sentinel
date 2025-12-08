# Threat Intelligence Upload API (Preview)

| | |
|----------|-------|
| **Connector ID** | `ThreatIntelligenceUploadIndicatorsAPI` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ThreatIntelIndicators`](../tables-index.md#threatintelindicators), [`ThreatIntelObjects`](../tables-index.md#threatintelobjects), [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [Threat Intelligence](../solutions/threat-intelligence.md), [Threat Intelligence (NEW)](../solutions/threat-intelligence-(new).md) |
| **Connector Definition Files** | [template_ThreatIntelligenceUploadIndicators.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Data%20Connectors/template_ThreatIntelligenceUploadIndicators.json), [template_ThreatIntelligenceUploadIndicators_ForGov.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Data%20Connectors/template_ThreatIntelligenceUploadIndicators_ForGov.json) |

Microsoft Sentinel offers a data plane API to bring in threat intelligence from your Threat Intelligence Platform (TIP), such as Threat Connect, Palo Alto Networks MineMeld, MISP, or other integrated applications. Threat indicators can include IP addresses, domains, URLs, file hashes and email addresses. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2269830&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[← Back to Connectors Index](../connectors-index.md)
