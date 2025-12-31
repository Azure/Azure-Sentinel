# Doppel

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Doppel |
| **Support Tier** | Partner |
| **Support Link** | [https://www.doppel.com/request-a-demo](https://www.doppel.com/request-a-demo) |
| **Categories** | domains |
| **First Published** | 2024-11-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Doppel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Doppel) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Doppel Data Connector](../connectors/doppel-dataconnector.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`DoppelTable_CL`](../tables/doppeltable-cl.md) | [Doppel Data Connector](../connectors/doppel-dataconnector.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Doppel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Doppel/Workbooks/Doppel.json) | [`DoppelTable_CL`](../tables/doppeltable-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** |                 **Change History**                  |
|-------------|--------------------------------|-----------------------------------------------------|
| 3.0.1       | 05-03-2025                     | Fixed typo error in **Data Connector**.             | 
| 3.0.0       | 03-12-2024                     | Initial Solution Release.                            |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
