# Illumio Core

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Core](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Core) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Illumio Core via Legacy Agent](../connectors/illumiocore.md)
- [[Deprecated] Illumio Core via AMA](../connectors/illumiocoreama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Illumio Core via AMA](../connectors/illumiocoreama.md), [[Deprecated] Illumio Core via Legacy Agent](../connectors/illumiocore.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [IllumioCoreEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Core/Parsers/IllumioCoreEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                  |
|-------------|--------------------------------|-----------------------------------------------------|
| 3.0.3       | 27-11-2024                     | Removed Deprecated **Data Connectors**              |
| 3.0.2       | 15-07-2024                     | Deprecating data connector                          |  
| 3.0.1       | 12-09-2023                     | Addition of new Illumio Core AMA **Data Connector** |  
| 3.0.0       | 24-07-2023                     | Corrected the links in the solution.  	             |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
