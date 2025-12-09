# Threat Intelligence Platforms

| | |
|----------|-------|
| **Connector ID** | `ThreatIntelligence` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog), [`ThreatIntelIndicators`](../tables-index.md#threatintelindicators), [`ThreatIntelObjects`](../tables-index.md#threatintelobjects), [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [Threat Intelligence](../solutions/threat-intelligence.md), [Threat Intelligence (NEW)](../solutions/threat-intelligence-(new).md) |
| **Connector Definition Files** | [template_ThreatIntelligence.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Data%20Connectors/template_ThreatIntelligence.json) |

Microsoft Sentinel integrates with Microsoft Graph Security API data sources to enable monitoring, alerting, and hunting using your threat intelligence. Use this connector to send threat indicators to Microsoft Sentinel from your Threat Intelligence Platform (TIP), such as Threat Connect, Palo Alto Networks MindMeld, MISP, or other integrated applications. Threat indicators can include IP addresses, domains, URLs, and file hashes. For more information, see the [Microsoft Sentinel documentation >](https://go.microsoft.com/fwlink/p/?linkid=2223729&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[← Back to Connectors Index](../connectors-index.md)
