# Talon

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Talon Security |
| **Support Tier** | Partner |
| **Support Link** | [https://docs.console.talon-sec.com/](https://docs.console.talon-sec.com/) |
| **Categories** | domains |
| **First Published** | 2023-01-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Talon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Talon) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Talon Insights](../connectors/talonlogs.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Talon_CL`](../tables/talon-cl.md) | [Talon Insights](../connectors/talonlogs.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [TalonInsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Talon/Workbooks/TalonInsights.json) | [`Talon_CL`](../tables/talon-cl.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
