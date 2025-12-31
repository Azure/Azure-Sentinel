# Blackberry CylancePROTECT

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Blackberry%20CylancePROTECT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Blackberry%20CylancePROTECT) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Blackberry CylancePROTECT](../connectors/blackberrycylanceprotect.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Blackberry CylancePROTECT](../connectors/blackberrycylanceprotect.md) | - |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 2 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CylancePROTECT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Blackberry%20CylancePROTECT/Parsers/CylancePROTECT.yaml) | - | - |
| [CylancePROTECT-old](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Blackberry%20CylancePROTECT/Parsers/CylancePROTECT-old.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 23-12-2024                     | Removed Deprecated **Data connector**       |
| 3.0.0       | 18-07-2024                     | Deprecating data connectors                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
