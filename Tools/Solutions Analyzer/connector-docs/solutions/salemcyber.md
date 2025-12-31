# SalemCyber

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Salem Cyber |
| **Support Tier** | Partner |
| **Support Link** | [https://www.salemcyber.com/contact](https://www.salemcyber.com/contact) |
| **Categories** | domains |
| **First Published** | 2023-07-21 |
| **Last Updated** | 2023-07-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SalemCyber](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SalemCyber) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`SalemAlerts_CL`](../tables/salemalerts-cl.md) | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |
| Playbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SalemDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SalemCyber/Workbooks/SalemDashboard.json) | [`SalemAlerts_CL`](../tables/salemalerts-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Send-Sentinel-Alerts-to-Salem](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SalemCyber/Playbooks/SendAlertToSalem/azuredeploy.json) | Use this playbook to send Microsoft Sentinel alerts to Salem Virtual Cyber Analyst | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       |     14-07-2023                 | Initial Solution Release                     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
