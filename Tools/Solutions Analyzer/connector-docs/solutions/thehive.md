# TheHive

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [TheHive Project - TheHive](../connectors/thehiveprojectthehive.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`TheHive_CL`](../tables/thehive-cl.md) | [TheHive Project - TheHive](../connectors/thehiveprojectthehive.md) | - |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 3 |
| Parsers | 1 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [The Hive - Create alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive/Playbooks/TheHive-CreateAlert/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | - |
| [The Hive - Create case](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive/Playbooks/TheHive-CreateCase/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | - |
| [The Hive - Lock user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive/Playbooks/TheHive-LockUser/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [TheHive](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive/Parsers/TheHive.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.0       | 05-09-2023                     | Manual deployment instructions updated for **Data Connector**		|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
