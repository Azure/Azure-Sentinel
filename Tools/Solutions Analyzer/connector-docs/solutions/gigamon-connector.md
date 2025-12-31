# Gigamon Connector

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Gigamon |
| **Support Tier** | Partner |
| **Support Link** | [https://www.gigamon.com/](https://www.gigamon.com/) |
| **Categories** | domains |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Gigamon%20Connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Gigamon%20Connector) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Gigamon AMX Data Connector](../connectors/gigamondataconnector.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Gigamon_CL`](../tables/gigamon-cl.md) | [Gigamon AMX Data Connector](../connectors/gigamondataconnector.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Gigamon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Gigamon%20Connector/Workbooks/Gigamon.json) | [`Gigamon_CL`](../tables/gigamon-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 25-10-2023                     | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
