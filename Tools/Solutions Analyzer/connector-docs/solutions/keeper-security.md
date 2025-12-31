# Keeper Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Keeper Security |
| **Support Tier** | Partner |
| **Support Link** | [https://www.keepersecurity.com](https://www.keepersecurity.com) |
| **Categories** | domains |
| **First Published** | 2025-06-03 |
| **Last Updated** | 2025-06-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Keeper Security Push Connector](../connectors/keepersecuritypush2.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`KeeperSecurityEventNewLogs_CL`](../tables/keepersecurityeventnewlogs-cl.md) | [Keeper Security Push Connector](../connectors/keepersecuritypush2.md) | Analytics, Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Keeper Security - Password Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security/Analytic%20Rules/Keeper%20Security%20-%20Alternate%20Master%20Password.yaml) | Informational | Persistence | [`KeeperSecurityEventNewLogs_CL`](../tables/keepersecurityeventnewlogs-cl.md) |
| [Keeper Security - User MFA Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security/Analytic%20Rules/Keeper%20Security%20-%20User%20MFA%20Changed.yaml) | Informational | Persistence | [`KeeperSecurityEventNewLogs_CL`](../tables/keepersecurityeventnewlogs-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [KeeperSecurityDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security/Workbooks/KeeperSecurityDashboard.json) | [`KeeperSecurityEventNewLogs_CL`](../tables/keepersecurityeventnewlogs-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                     |
|-------------|--------------------------------|----------------------------------------|
| 3.0.1       | 25-07-2025                     | Added new **Analytic Rules** and **Workbook**  |
| 3.0.0       | 11-06-2025                     | Initial Solution Release with KeeperSecurity **Data Connector** CCP. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
