# AristaAwakeSecurity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Arista - Awake Security |
| **Support Tier** | Partner |
| **Support Link** | [https://awakesecurity.com/](https://awakesecurity.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Awake Security via Legacy Agent](../connectors/aristaawakesecurity.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Awake Security via Legacy Agent](../connectors/aristaawakesecurity.md) | Analytics |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 3 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Awake Security - High Match Counts By Device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Analytic%20Rules/HighMatchCountsByDevice.yaml) | Medium | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Awake Security - High Severity Matches By Device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Analytic%20Rules/HighSeverityMatchesByDevice.yaml) | Medium | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Awake Security - Model With Multiple Destinations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Analytic%20Rules/ModelMatchesWithMultipleDestinationsByDevice.yaml) | Medium | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AristaAwakeSecurityWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Workbooks/AristaAwakeSecurityWorkbook.json) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.1       | 03-01-2025                     | Removed Deprecated **Data connector**          |
| 3.0.0       | 09-07-2024                     | Deprecating data connectors.                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
