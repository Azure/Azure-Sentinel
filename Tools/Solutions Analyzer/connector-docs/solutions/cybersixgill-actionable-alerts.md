# Cybersixgill-Actionable-Alerts

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cybersixgill |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cybersixgill.com/](https://www.cybersixgill.com/) |
| **Categories** | domains |
| **First Published** | 2023-02-27 |
| **Last Updated** | 2024-09-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cybersixgill-Actionable-Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cybersixgill-Actionable-Alerts) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Cybersixgill Actionable Alerts](../connectors/cybersixgillactionablealerts.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyberSixgill_Alerts_CL`](../tables/cybersixgill-alerts-cl.md) | [Cybersixgill Actionable Alerts](../connectors/cybersixgillactionablealerts.md) | Hunting, Workbooks |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 2 |
| Playbooks | 2 |
| Hunting Queries | 1 |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Cybersixgill Actionable alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cybersixgill-Actionable-Alerts/Hunting%20Queries/ActionableAlerts.yaml) | - | [`CyberSixgill_Alerts_CL`](../tables/cybersixgill-alerts-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ActionableAlertsDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cybersixgill-Actionable-Alerts/Workbooks/ActionableAlertsDashboard.json) | [`CyberSixgill_Alerts_CL`](../tables/cybersixgill-alerts-cl.md) |
| [ActionableAlertsList](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cybersixgill-Actionable-Alerts/Workbooks/ActionableAlertsList.json) | [`CyberSixgill_Alerts_CL`](../tables/cybersixgill-alerts-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Cybersixgill-Alert-Status-Update](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cybersixgill-Actionable-Alerts/Playbooks/CybersixgillAlertStatusUpdate/azuredeploy.json) | This playbook will update status of Cybersixgill Alerts when respective incident status is updated i... | - |
| [Delete-Cybersixgill-Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cybersixgill-Actionable-Alerts/Playbooks/DeleteCybersixgillAlert/azuredeploy.json) | This playbook will delete Alert on Cybersixgill portal when resective Incident is deleted in Microso... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 02-09-2024                     | Updated the python runtime version to 3.11  |
| 3.0.0       | 20-02-2024                     | Replaced Hyperlinks with Shortlinks (aka.ms) in Data Connector |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
