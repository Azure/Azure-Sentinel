# Sophos XG Firewall

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Sophos XG Firewall](../connectors/sophosxgfirewall.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Sophos XG Firewall](../connectors/sophosxgfirewall.md) | Analytics, Workbooks |

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
| [Excessive Amount of Denied Connections from a Single Source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall/Analytic%20Rules/ExcessiveAmountofDeniedConnectionsfromASingleSource.yaml) | Medium | Impact | [`Syslog`](../tables/syslog.md) |
| [Port Scan Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall/Analytic%20Rules/PortScanDetected.yaml) | Medium | Discovery | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SophosXGFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall/Workbooks/SophosXGFirewall.json) | [`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SophosXGFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall/Parsers/SophosXGFirewall.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                  |
|-------------|--------------------------------|-------------------------------------------------------------------------------------|
| 3.0.1       | 09-12-2024                     | Rmoved Deprecated **Data Connector**                                                |
|             |                                | Updated SophosXGFirewall.json **Workbook** to fix missing fields                    |
| 3.0.0       | 01-08-2024                     | Update **Parser** as part of Syslog migration </br> Deprecating **Data Connectors** |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
