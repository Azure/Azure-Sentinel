# Exabeam Advanced Analytics

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Exabeam%20Advanced%20Analytics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Exabeam%20Advanced%20Analytics) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Exabeam Advanced Analytics](../connectors/exabeam.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Exabeam Advanced Analytics](../connectors/exabeam.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ExabeamEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Exabeam%20Advanced%20Analytics/Parsers/ExabeamEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                 |
|-------------|-------------------------------|-----------------------------------------------------|
| 3.0.2 	  | 02-01-2025 					  | Removed Deprecated **Data connector** 				|
| 3.0.1       | 27-07-2024                    | Deprecating data connectors                         |
| 3.0.0       | 24-07-2023                    | Corrected the links in the solution.		        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
