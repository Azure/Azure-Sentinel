# ISC Bind

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-09-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ISC%20Bind](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ISC%20Bind) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] ISC Bind](../connectors/iscbind.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] ISC Bind](../connectors/iscbind.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ISCBind](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ISC%20Bind/Parsers/ISCBind.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 27-12-2024                     |     Removed Deprecated **Data connector**                          |
| 3.0.1       | 24-07-2024                     |     Deprecated Data connectors                                     |
| 3.0.0       | 09-10-2023                     |     Corrected the links in the solution                            |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
