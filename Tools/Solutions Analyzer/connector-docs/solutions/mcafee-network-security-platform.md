# McAfee Network Security Platform

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20Network%20Security%20Platform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20Network%20Security%20Platform) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] McAfee Network Security Platform](../connectors/mcafeensp.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] McAfee Network Security Platform](../connectors/mcafeensp.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [McAfeeNSPEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20Network%20Security%20Platform/Parsers/McAfeeNSPEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                               |
|-------------|--------------------------------|--------------------------------------------------|
| 3.0.1       | 27-12-2024                     | Removed Deprecated **Data connector**            |
| 3.0.0       | 23-07-2024                     | Deprecated Data connectors  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
