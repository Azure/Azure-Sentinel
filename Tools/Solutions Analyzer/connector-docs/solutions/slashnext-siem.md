# SlashNext SIEM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SlashNext |
| **Support Tier** | Partner |
| **Support Link** | [https://slashnext.com/support](https://slashnext.com/support) |
| **Categories** | domains |
| **First Published** | 2023-05-26 |
| **Last Updated** | 2023-06-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext%20SIEM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext%20SIEM) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`SlashNext_CL`](../tables/slashnext-cl.md) | Playbooks (writes) |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 1 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SlashNext Security Events for Microsoft Sentinel - Get customer incidents and log](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext%20SIEM/Playbooks/SlashNextSecurityEventForMSSentinel/azuredeploy.json) | The playbook will run after every 3 mintues to get list of events occured to a customer in that time... | [`SlashNext_CL`](../tables/slashnext-cl.md) *(write)* |

## Release Notes

| **Version** | **Date**   | **Change History**               |
|-------------|------------|----------------------------------|
| 3.1.0       | 10-07-2024 | Integrated API for detailed data |
| 3.0.0       | 25-04-2024 | Initial Solution Release         |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
