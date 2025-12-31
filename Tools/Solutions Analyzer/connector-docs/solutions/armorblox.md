# Armorblox

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Armorblox |
| **Support Tier** | Partner |
| **Support Link** | [https://www.armorblox.com/contact/](https://www.armorblox.com/contact/) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armorblox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armorblox) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Armorblox](../connectors/armorblox.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Armorblox_CL`](../tables/armorblox-cl.md) | [Armorblox](../connectors/armorblox.md) | Analytics, Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Armorblox Needs Review Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armorblox/Analytic%20Rules/ArmorbloxNeedsReviewAlert.yaml) | Medium | - | [`Armorblox_CL`](../tables/armorblox-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ArmorbloxOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armorblox/Workbooks/ArmorbloxOverview.json) | [`Armorblox_CL`](../tables/armorblox-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Needs-Review-Incident-Email-Notification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armorblox/Playbooks/Needs-Review-Incident-Email-Notification/azuredeploy.json) | This playbook will send an email notification when a new incident is created in Microsoft Sentinel. | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       |     11-09-2024                 | Updated the python runtime version to 3.11  |
| 3.0.0       |     23-11-2023                 | Added entity mapping in **Analytical Rule** [Armorblox Needs Review Alert] |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
