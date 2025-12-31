# Delinea Secret Server

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Delinea |
| **Support Tier** | Partner |
| **Support Link** | [https://delinea.com/support/](https://delinea.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Delinea Secret Server via AMA](../connectors/delineasecretserverama.md)
- [[Deprecated] Delinea Secret Server via Legacy Agent](../connectors/delineasecretserver-cef.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Delinea Secret Server via AMA](../connectors/delineasecretserverama.md), [[Deprecated] Delinea Secret Server via Legacy Agent](../connectors/delineasecretserver-cef.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [DelineaWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server/Workbooks/DelineaWorkbook.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 11-07-2024                     |    Deprecating data connectors                                     |
| 3.0.0       | 20-09-2023                     |	Addition of new Delinea Secret Server AMA **Data Connector**    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
