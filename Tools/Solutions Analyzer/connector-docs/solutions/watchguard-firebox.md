# Watchguard Firebox

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | WatchGuard |
| **Support Tier** | Partner |
| **Support Link** | [https://www.watchguard.com/wgrd-support/contact-support](https://www.watchguard.com/wgrd-support/contact-support) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Watchguard%20Firebox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Watchguard%20Firebox) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] WatchGuard Firebox](../connectors/watchguardfirebox.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] WatchGuard Firebox](../connectors/watchguardfirebox.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [WatchGuardFirebox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Watchguard%20Firebox/Parsers/WatchGuardFirebox.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.0       | 18-07-2024                     |  Deprecating data connectors         |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
