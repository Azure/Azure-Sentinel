# iboss

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | iboss |
| **Support Tier** | Partner |
| **Support Link** | [https://www.iboss.com/contact-us/](https://www.iboss.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-02-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] iboss via Legacy Agent](../connectors/iboss.md)
- [iboss via AMA](../connectors/ibossama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] iboss via Legacy Agent](../connectors/iboss.md), [iboss via AMA](../connectors/ibossama.md) | Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 2 |
| Parsers | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ibossMalwareAndC2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss/Workbooks/ibossMalwareAndC2.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ibossWebUsage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss/Workbooks/ibossWebUsage.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ibossUrlEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss/Parsers/ibossUrlEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.1.2       | 07-01-2025                     |    Removed Deprecated **Data connector**                           |
| 3.1.1       | 18-09-2024                     |    Updated AMA and legacy OMS connector to use new iboss field     |
| 3.1.0       | 05-09-2024                     |    Updated AMA connector with iboss specific instructions          |
| 3.0.1       | 12-07-2024                     |    Deprecating data connectors                                     |
| 3.0.0       | 20-09-2023                     |	Addition of new Iboss AMA **Data Connector**                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
