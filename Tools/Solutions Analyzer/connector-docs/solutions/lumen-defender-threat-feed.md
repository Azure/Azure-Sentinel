# Lumen Defender Threat Feed

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Lumen Technologies, Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://www.lumen.com/en-us/contact-us/support.html](https://www.lumen.com/en-us/contact-us/support.html) |
| **Categories** | domains |
| **First Published** | 2025-09-12 |
| **Last Updated** | 2025-09-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Lumen Defender Threat Feed Data Connector](../connectors/lumenthreatfeedconnector.md)

**Publisher:** Lumen Technologies, Inc.

The [Lumen Defender Threat Feed](https://bll-analytics.mss.lumen.com/analytics) connector provides the capability to ingest STIX-formatted threat intelligence indicators from Lumen's Black Lotus Labs research team into Microsoft Sentinel. The connector automatically downloads and uploads daily threat intelligence indicators including IPv4 addresses and domains to the ThreatIntelIndicators table via the STIX Objects Upload API.

| | |
|--------------------------|---|
| **Tables Ingested** | `ThreatIntelIndicators` |
| **Connector Definition Files** | [LumenThreatFeedConnector_ConnectorUI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Data%20Connectors/LumenThreatFeed/LumenThreatFeedConnector_ConnectorUI.json) |

[→ View full connector details](../connectors/lumenthreatfeedconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ThreatIntelIndicators` | [Lumen Defender Threat Feed Data Connector](../connectors/lumenthreatfeedconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
