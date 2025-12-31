# BETTER Mobile Threat Defense (MTD)

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Better Mobile Security Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://www.better.mobi/about#contact-us](https://www.better.mobi/about#contact-us) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BETTER%20Mobile%20Threat%20Defense%20%28MTD%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BETTER%20Mobile%20Threat%20Defense%20%28MTD%29) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [BETTER Mobile Threat Defense (MTD)](../connectors/bettermtd.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`BetterMTDAppLog_CL`](../tables/bettermtdapplog-cl.md) | [BETTER Mobile Threat Defense (MTD)](../connectors/bettermtd.md) | Workbooks |
| [`BetterMTDDeviceLog_CL`](../tables/bettermtddevicelog-cl.md) | [BETTER Mobile Threat Defense (MTD)](../connectors/bettermtd.md) | Workbooks |
| [`BetterMTDIncidentLog_CL`](../tables/bettermtdincidentlog-cl.md) | [BETTER Mobile Threat Defense (MTD)](../connectors/bettermtd.md) | Workbooks |
| [`BetterMTDNetflowLog_CL`](../tables/bettermtdnetflowlog-cl.md) | [BETTER Mobile Threat Defense (MTD)](../connectors/bettermtd.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [BETTER_MTD_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BETTER%20Mobile%20Threat%20Defense%20%28MTD%29/Workbooks/BETTER_MTD_Workbook.json) | [`BetterMTDAppLog_CL`](../tables/bettermtdapplog-cl.md)<br>[`BetterMTDDeviceLog_CL`](../tables/bettermtddevicelog-cl.md)<br>[`BetterMTDIncidentLog_CL`](../tables/bettermtdincidentlog-cl.md)<br>[`BetterMTDNetflowLog_CL`](../tables/bettermtdnetflowlog-cl.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
