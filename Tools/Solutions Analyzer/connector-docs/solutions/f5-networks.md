# F5 Networks

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | F5 |
| **Support Tier** | Partner |
| **Support Link** | [https://www.f5.com/services/support](https://www.f5.com/services/support) |
| **Categories** | domains |
| **First Published** | 2022-05-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20Networks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20Networks) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] F5 Networks via Legacy Agent](../connectors/f5.md)
- [[Deprecated] F5 Networks via AMA](../connectors/f5ama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] F5 Networks via AMA](../connectors/f5ama.md), [[Deprecated] F5 Networks via Legacy Agent](../connectors/f5.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 11-07-2024                     |    Deprecating data connectors                                     |
| 3.0.0       | 29-09-2023                     |	Addition of new F5 Networks AMA **Data Connector**              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
