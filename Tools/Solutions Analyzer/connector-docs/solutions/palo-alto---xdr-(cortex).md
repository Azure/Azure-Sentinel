# Palo Alto - XDR (Cortex)

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** |  |
| **Support Tier** |  |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20-%20XDR%20%28Cortex%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20-%20XDR%20%28Cortex%29) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Palo Alto Networks Cortex XDR](../connectors/paloaltonetworkscortex.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [Palo Alto Networks Cortex XDR](../connectors/paloaltonetworkscortex.md) | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |
| Playbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [PaloAltoXDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20-%20XDR%20%28Cortex%29/Workbooks/PaloAltoXDR.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [PaloAltoXDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20-%20XDR%20%28Cortex%29/Playbooks/azuredeploy.json) | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) *(read)* |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
