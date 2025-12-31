# MimecastTIRegional

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Mimecast |
| **Support Tier** | Partner |
| **Support Link** | [https://mimecastsupport.zendesk.com/](https://mimecastsupport.zendesk.com/) |
| **Categories** | domains |
| **First Published** | 2023-08-23 |
| **Last Updated** | 2023-09-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTIRegional](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTIRegional) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Event`](../tables/event.md) | [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md) | - |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [MimecastTIRegional](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTIRegional/Workbooks/MimecastTIRegional.json) | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 06-03-2025                     | Solution Deprecated   |
| 3.0.1       | 05-12-2023                     | Enhanced **Dataconnector** to use existing workspace and updated checkpoint mechanism |
| 3.0.0       | 23-08-2023                     | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
