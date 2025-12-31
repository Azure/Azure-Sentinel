# ExtraHop Reveal(x)

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | ExtraHop |
| **Support Tier** | Partner |
| **Support Link** | [https://www.extrahop.com/support/](https://www.extrahop.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] ExtraHop Reveal(x) via Legacy Agent](../connectors/extrahopnetworks.md)
- [[Deprecated] ExtraHop Reveal(x) via AMA](../connectors/extrahopnetworksama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] ExtraHop Reveal(x) via AMA](../connectors/extrahopnetworksama.md), [[Deprecated] ExtraHop Reveal(x) via Legacy Agent](../connectors/extrahopnetworks.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ExtraHopDetectionSummary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29/Workbooks/ExtraHopDetectionSummary.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 11-07-2024                     |    Deprecating data connectors                                     |
| 3.0.0       | 13-09-2023                     |	Addition of new ExtraHop Reveal(x) AMA **Data Connector**       |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
