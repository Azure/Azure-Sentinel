# GreyNoiseThreatIntelligence

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | GreyNoise |
| **Support Tier** | Partner |
| **Support Link** | [https://www.greynoise.io/contact/general](https://www.greynoise.io/contact/general) |
| **Categories** | domains |
| **First Published** | 2023-09-05 |
| **Last Updated** | 2025-07-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### GreyNoise Threat Intelligence

**Publisher:** GreyNoise, Inc. and BlueCycle LLC

This Data Connector installs an Azure Function app to download GreyNoise indicators once per day and inserts them into the ThreatIntelligenceIndicator table in Microsoft Sentinel.

**Tables Ingested:**

- `ThreatIntelligenceIndicator`

**Connector Definition Files:**

- [GreyNoiseConnector_UploadIndicatorsAPI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Data%20Connectors/GreyNoiseConnector_UploadIndicatorsAPI.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ThreatIntelligenceIndicator` | GreyNoise Threat Intelligence |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n