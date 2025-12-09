# Lumen Defender Threat Feed Data Connector

| | |
|----------|-------|
| **Connector ID** | `LumenThreatFeedConnector` |
| **Publisher** | Lumen Technologies, Inc. |
| **Tables Ingested** | [`ThreatIntelIndicators`](../tables-index.md#threatintelindicators) |
| **Used in Solutions** | [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md) |
| **Connector Definition Files** | [LumenThreatFeedConnector_ConnectorUI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Data%20Connectors/LumenThreatFeed/LumenThreatFeedConnector_ConnectorUI.json) |

The [Lumen Defender Threat Feed](https://bll-analytics.mss.lumen.com/analytics) connector provides the capability to ingest STIX-formatted threat intelligence indicators from Lumen's Black Lotus Labs research team into Microsoft Sentinel. The connector automatically downloads and uploads daily threat intelligence indicators including IPv4 addresses and domains to the ThreatIntelIndicators table via the STIX Objects Upload API.

[← Back to Connectors Index](../connectors-index.md)
