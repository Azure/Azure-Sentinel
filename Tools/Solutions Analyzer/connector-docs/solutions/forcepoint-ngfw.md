# Forcepoint NGFW

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Forcepoint NGFW via Legacy Agent](../connectors/forcepointngfw.md)
- [[Deprecated] Forcepoint NGFW via AMA](../connectors/forcepointngfwama.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Forcepoint NGFW via AMA](../connectors/forcepointngfwama.md), [[Deprecated] Forcepoint NGFW via Legacy Agent](../connectors/forcepointngfw.md) | Workbooks |
| [`IPs`](../tables/ips.md) | - | Workbooks |
| [`Perf`](../tables/perf.md) | - | Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | - | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 2 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ForcepointNGFW](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW/Workbooks/ForcepointNGFW.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ForcepointNGFWAdvanced](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW/Workbooks/ForcepointNGFWAdvanced.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`IPs`](../tables/ips.md)<br>[`Perf`](../tables/perf.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 19-11-2024                     |    Removed Deprecated **Data Connectors**                          |
| 3.0.1       | 15-07-2024                     |	Deprecating data connectors                                     |
| 3.0.0       | 29-08-2023                     |	Addition of new Forcepoint NGFW AMA **Data Connector**          |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
