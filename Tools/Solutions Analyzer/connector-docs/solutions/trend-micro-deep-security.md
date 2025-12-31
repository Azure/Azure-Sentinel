# Trend Micro Deep Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Trend Micro |
| **Support Tier** | Partner |
| **Support Link** | [https://success.trendmicro.com/dcx/s/?language=en_US](https://success.trendmicro.com/dcx/s/?language=en_US) |
| **Categories** | domains |
| **First Published** | 2022-05-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Deep%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Deep%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Trend Micro Deep Security via Legacy](../connectors/trendmicro.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Trend Micro Deep Security via Legacy](../connectors/trendmicro.md) | Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 2 |
| Parsers | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [TrendMicroDeepSecurityAttackActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Deep%20Security/Workbooks/TrendMicroDeepSecurityAttackActivity.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [TrendMicroDeepSecurityOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Deep%20Security/Workbooks/TrendMicroDeepSecurityOverview.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [TrendMicroDeepSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Deep%20Security/Parsers/TrendMicroDeepSecurity.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 03-01-2025                     | Removed Deprecated **Data connector**                              |
| 3.0.0       | 27-06-2024                     | Deprecating data connectors     |
| 2.0.1       | 11-11-2022                     | Updated OfferId     |
| 2.0.0       | 20-07-2022                     | Initial Package     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
