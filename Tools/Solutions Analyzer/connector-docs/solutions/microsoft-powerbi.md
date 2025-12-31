# Microsoft PowerBI

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20PowerBI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20PowerBI) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft PowerBI](../connectors/officepowerbi.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`PowerBIActivity`](../tables/powerbiactivity.md) | [Microsoft PowerBI](../connectors/officepowerbi.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [MicrosoftPowerBIActivityWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20PowerBI/Workbooks/MicrosoftPowerBIActivityWorkbook.json) | [`PowerBIActivity`](../tables/powerbiactivity.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
