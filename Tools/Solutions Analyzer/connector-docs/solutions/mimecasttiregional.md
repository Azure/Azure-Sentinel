# MimecastTIRegional

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Mimecast |
| **Support Tier** | Partner |
| **Support Link** | [https://mimecastsupport.zendesk.com/](https://mimecastsupport.zendesk.com/) |
| **Categories** | domains |
| **First Published** | 2023-08-23 |
| **Last Updated** | 2023-09-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTIRegional](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTIRegional) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md)

**Publisher:** Mimecast

The data connector for Mimecast Intelligence for Microsoft provides regional threat intelligence curated from Mimecast’s email inspection technologies with pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times.  

Mimecast products and features required: 

- Mimecast Secure Email Gateway 

- Mimecast Threat Intelligence



| | |
|--------------------------|---|
| **Tables Ingested** | `Event` |
| | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [MimecastTIRegional_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTIRegional/Data%20Connectors/MimecastTIRegional_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/mimecasttiregionalconnectorazurefunctions.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Event` | [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md) |
| `ThreatIntelligenceIndicator` | [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md) |

[← Back to Solutions Index](../solutions-index.md)
