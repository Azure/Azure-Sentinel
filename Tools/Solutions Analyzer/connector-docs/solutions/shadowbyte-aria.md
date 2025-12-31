# ShadowByte Aria

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Shadowbyte |
| **Support Tier** | Partner |
| **Support Link** | [https://shadowbyte.com/products/aria/](https://shadowbyte.com/products/aria/) |
| **Categories** | domains |
| **First Published** | 2021-12-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ShadowByte%20Aria](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ShadowByte%20Aria) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`ShadowByteAriaForums_CL`](../tables/shadowbyteariaforums-cl.md) | Playbooks (writes) |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 2 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Enrich Incidents - ShadowByte Aria](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ShadowByte%20Aria/Playbooks/ShadowByte_Aria_Enrich_Incidents/azuredeploy.json) | This playbook updates the Incident with the brach details if an account has been compromised. | - |
| [Search for Breaches - ShadowByte Aria](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ShadowByte%20Aria/Playbooks/ShadowByte_Aria_Search_for_Breaches/azuredeploy.json) | This playbook updates the Incident with the brach details if an account has been compromised. | [`ShadowByteAriaForums_CL`](../tables/shadowbyteariaforums-cl.md) *(write)* |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
