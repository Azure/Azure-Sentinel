# Valence Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Valence Security |
| **Support Tier** | Partner |
| **Support Link** | [https://www.valencesecurity.com/](https://www.valencesecurity.com/) |
| **Categories** | domains |
| **First Published** | 2023-11-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Valence%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Valence%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [SaaS Security](../connectors/valencesecurity.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ValenceAlert_CL`](../tables/valencealert-cl.md) | [SaaS Security](../connectors/valencesecurity.md) | Analytics, Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Valence Security Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Valence%20Security/Analytic%20Rules/ValenceAlerts.yaml) | High | - | [`ValenceAlert_CL`](../tables/valencealert-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ValenceAlertsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Valence%20Security/Workbooks/ValenceAlertsWorkbook.json) | [`ValenceAlert_CL`](../tables/valencealert-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                |
|-------------|--------------------------------|-----------------------------------|
|  3.0.0      |  27-11-2023                    |  Initial Solution Release         |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
