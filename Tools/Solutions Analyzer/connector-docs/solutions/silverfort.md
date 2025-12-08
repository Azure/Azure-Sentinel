# Silverfort

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Silverfort |
| **Support Tier** | Partner |
| **Support Link** | [https://www.silverfort.com/customer-success/#support](https://www.silverfort.com/customer-success/#support) |
| **Categories** | domains |
| **First Published** | 2024-09-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Silverfort Admin Console](../connectors/silverfortama.md)

**Publisher:** Silverfort

The [Silverfort](https://silverfort.com) ITDR Admin Console connector solution allows ingestion of Silverfort events and logging into Microsoft Sentinel.

 Silverfort provides syslog based events and logging using Common Event Format (CEF). By forwarding your Silverfort ITDR Admin Console CEF data into Microsoft Sentinel, you can take advantage of Sentinels's search & correlation, alerting, and threat intelligence enrichment on Silverfort data. 

 Please contact Silverfort or consult the Silverfort documentation for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [SilverfortAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Data%20Connectors/SilverfortAma.json) |

[→ View full connector details](../connectors/silverfortama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [Silverfort Admin Console](../connectors/silverfortama.md) |

[← Back to Solutions Index](../solutions-index.md)
