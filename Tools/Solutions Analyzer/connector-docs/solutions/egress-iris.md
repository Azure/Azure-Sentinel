# Egress Iris

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Egress Software Technologies Ltd |
| **Support Tier** | Partner |
| **Support Link** | [https://support.egress.com](https://support.egress.com) |
| **Categories** | domains |
| **First Published** | 2024-03-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Iris](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Iris) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Egress Iris Connector](../connectors/egresssiempolling.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`DefendAuditData`](../tables/defendauditdata.md) | [Egress Iris Connector](../connectors/egresssiempolling.md) | - |
| [`EgressEvents_CL`](../tables/egressevents-cl.md) | [Egress Iris Connector](../connectors/egresssiempolling.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [PreventWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Iris/Workbooks/PreventWorkbook.json) | [`EgressEvents_CL`](../tables/egressevents-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 17-04-2024                     | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
