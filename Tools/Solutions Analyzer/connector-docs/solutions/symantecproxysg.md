# SymantecProxySG

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2021-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Symantec ProxySG](../connectors/symantecproxysg.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Symantec ProxySG](../connectors/symantecproxysg.md) | Analytics, Workbooks |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Excessive Denied Proxy Traffic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG/Analytic%20Rules/ExcessiveDeniedProxyTraffic.yaml) | Low | DefenseEvasion, CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [User Accessed Suspicious URL Categories](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG/Analytic%20Rules/UserAccessedSuspiciousURLCategories.yaml) | Medium | InitialAccess, CommandAndControl | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SymantecProxySG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG/Workbooks/SymantecProxySG.json) | [`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SymantecProxySG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG/Parsers/SymantecProxySG.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       | 20-01-2025                     | Removed Custom Entity mappings from **Analytic rules**          |
| 3.0.2       | 24-12-2024                     |Removed Deprecated **Data Connector**        |
| 3.0.1       | 01-08-2024                     |Update **Parser** as part of Syslog migration                         |
|             |                                |Deprecating data connectors                                           |
| 3.0.0       | 06-11-2023                     | Modified the **Data Connector** with improved onboarding instructions and Optimized the **Parser** to process the logs with improved performance |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
