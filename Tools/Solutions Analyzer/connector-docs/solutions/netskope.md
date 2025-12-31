# Netskope

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Netskope |
| **Support Tier** | Partner |
| **Support Link** | [https://www.netskope.com/services#support](https://www.netskope.com/services#support) |
| **Categories** | domains |
| **First Published** | 2022-05-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskope](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskope) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Netskope](../connectors/netskope.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Netskope_Alerts_CL`](../tables/netskope-alerts-cl.md) | - | Workbooks |
| [`Netskope_CL`](../tables/netskope-cl.md) | [Netskope](../connectors/netskope.md) | - |
| [`Netskope_Events_CL`](../tables/netskope-events-cl.md) | - | Workbooks |
| [`Netskope_WebTX_CL`](../tables/netskope-webtx-cl.md) | - | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |
| Parsers | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [NetskopeEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskope/Workbooks/NetskopeEvents.json) | [`Netskope_Alerts_CL`](../tables/netskope-alerts-cl.md)<br>[`Netskope_Events_CL`](../tables/netskope-events-cl.md)<br>[`Netskope_WebTX_CL`](../tables/netskope-webtx-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Netskope](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskope/Parsers/Netskope.yaml) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
