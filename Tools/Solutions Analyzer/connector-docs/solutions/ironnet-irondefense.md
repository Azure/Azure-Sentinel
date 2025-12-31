# IronNet IronDefense

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [IronNet IronDefense](../connectors/ironnetirondefense.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [IronNet IronDefense](../connectors/ironnetirondefense.md) | Analytics, Workbooks |

## Content Items

This solution includes **6 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 3 |
| Workbooks | 2 |
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Create Incidents from IronDefense](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Analytic%20Rules/IronDefense_Detection_Query.yaml) | Medium | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [IronDefenseAlertDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Workbooks/IronDefenseAlertDashboard.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [IronDefenseAlertDetails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Workbooks/IronDefenseAlertDetails.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [IronNet_UpdateIronDefenseAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Playbooks/IronNet_UpdateIronDefenseAlerts/azuredeploy.json) | - | - |
| [IronNet_UpdateSentinelIncidents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Playbooks/IronNet_UpdateSentinelIncidents/azuredeploy.json) | - | - |
| [IronNet_Validate_IronNet_API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Playbooks/IronNet_Validate_IronNet_API/azuredeploy.json) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
