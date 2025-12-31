# CTERA

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CTERA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.ctera.com/](https://www.ctera.com/) |
| **Categories** | domains |
| **First Published** | 2024-07-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CTERA Syslog](../connectors/ctera.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [CTERA Syslog](../connectors/ctera.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 6 |
| Hunting Queries | 3 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Antivirus Detected an Infected File](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/InfectedFileDetected.yaml) | High | Impact | [`Syslog`](../tables/syslog.md) |
| [CTERA Mass Access Denied Detection Analytic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/MassAccessDenied.yaml) | High | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [CTERA Mass Deletions Detection Analytic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/MassDeletions.yaml) | High | Impact | [`Syslog`](../tables/syslog.md) |
| [CTERA Mass Permissions Changes Detection Analytic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/MassPermissionChanges.yaml) | High | PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |
| [Ransom Protect Detected a Ransomware Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/RansomwareDetected.yaml) | High | Impact | [`Syslog`](../tables/syslog.md) |
| [Ransom Protect User Blocked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/RansomwareUserBlocked.yaml) | High | Impact | [`Syslog`](../tables/syslog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [CTERA Batch Access Denied Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Hunting%20Queries/AccessDenied.yaml) | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [CTERA Batch File Deletions Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Hunting%20Queries/BatchDeletions.yaml) | Impact | [`Syslog`](../tables/syslog.md) |
| [CTERA Permission Change Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Hunting%20Queries/BatchPermissionChanges.yaml) | PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CTERA_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Workbooks/CTERA_Workbook.json) | [`Syslog`](../tables/syslog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                         |
|-------------|--------------------------------|--------------------------------------------|
| 3.0.1       | 05-12-2024                     | Update on existing **Hunting Queries** and new **Analytic Rules** |
| 3.0.0       | 21-10-2024                     | Initial Solution Release                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
