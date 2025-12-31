# Forcepoint CASB

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-05-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Forcepoint CASB via Legacy Agent](../connectors/forcepointcasb.md)
- [[Deprecated] Forcepoint CASB via AMA](../connectors/forcepointcasbama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Forcepoint CASB via AMA](../connectors/forcepointcasbama.md), [[Deprecated] Forcepoint CASB via Legacy Agent](../connectors/forcepointcasb.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ForcepointCASB](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB/Workbooks/ForcepointCASB.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 27-11-2024                     |    Removed Deprecated **Data Connectors**                          |
| 3.0.1       | 15-07-2024                     |	Deprecating data connectors                                     |
| 3.0.0       | 31-08-2023                     |	Addition of new Forcepoint CASB AMA **Data Connector**          |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
