# GreyNoise Threat Intelligence

| | |
|----------|-------|
| **Connector ID** | `GreyNoise2SentinelAPI` |
| **Publisher** | GreyNoise, Inc. and BlueCycle LLC |
| **Tables Ingested** | [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md) |
| **Connector Definition Files** | [GreyNoiseConnector_UploadIndicatorsAPI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Data%20Connectors/GreyNoiseConnector_UploadIndicatorsAPI.json) |

This Data Connector installs an Azure Function app to download GreyNoise indicators once per day and inserts them into the ThreatIntelligenceIndicator table in Microsoft Sentinel.

[← Back to Connectors Index](../connectors-index.md)
