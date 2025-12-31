# Trend Micro TippingPoint

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Trend Micro |
| **Support Tier** | Partner |
| **Support Link** | [https://success.trendmicro.com/dcx/s/contactus?language=en_US](https://success.trendmicro.com/dcx/s/contactus?language=en_US) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20TippingPoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20TippingPoint) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Trend Micro TippingPoint via Legacy](../connectors/trendmicrotippingpoint.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Trend Micro TippingPoint via Legacy](../connectors/trendmicrotippingpoint.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [TrendMicroTippingPoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20TippingPoint/Parsers/TrendMicroTippingPoint.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 06-01-2025                     | Removed Deprecated **Data connector**                              |
| 3.0.0       | 27-06-2024                     | Deprecating data connectors                                        |
| 2.0.2       | 30-05-2023                     | Updated Package                                                    |
| 2.0.1       | 11-11-2022                     | Initial Release                                                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
