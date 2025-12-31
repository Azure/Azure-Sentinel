# ForgeRock Common Audit for CEF

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Forgerock |
| **Support Tier** | Partner |
| **Support Link** | [https://www.forgerock.com/support](https://www.forgerock.com/support) |
| **Categories** | domains |
| **First Published** | 2022-05-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForgeRock%20Common%20Audit%20for%20CEF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForgeRock%20Common%20Audit%20for%20CEF) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] ForgeRock Identity Platform](../connectors/forgerock.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] ForgeRock Identity Platform](../connectors/forgerock.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ForgeRockParser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForgeRock%20Common%20Audit%20for%20CEF/Parsers/ForgeRockParser.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.0       | 01-07-2024                     |  Deprecating data connectors                                          |
| 2.0.0       | 06-05-2023                     |  Initial Solution Release                                          |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
