# Forcepoint CSG

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-05-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Forcepoint CSG via Legacy Agent](../connectors/forcepointcsg.md)
- [[Deprecated] Forcepoint CSG via AMA](../connectors/forcepointcsgama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Forcepoint CSG via AMA](../connectors/forcepointcsgama.md), [[Deprecated] Forcepoint CSG via Legacy Agent](../connectors/forcepointcsg.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ForcepointCloudSecuirtyGateway](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG/Workbooks/ForcepointCloudSecuirtyGateway.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 19-11-2024                     |    Removed Deprecated **Data Connectors**                          |
| 3.0.2       | 15-07-2024                     |	Deprecating data connectors                                     |
| 3.0.1       | 19-12-2023                     |	Workbook moved from standalone to solution and repackage        |
| 3.0.0       | 11-09-2023                     |	Addition of new Forcepoint CSG AMA **Data Connector**           |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
