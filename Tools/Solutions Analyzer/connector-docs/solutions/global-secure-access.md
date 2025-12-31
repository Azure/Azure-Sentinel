# Global Secure Access

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://learn.microsoft.com/en-us/entra/global-secure-access/overview-what-is-global-secure-access](https://learn.microsoft.com/en-us/entra/global-secure-access/overview-what-is-global-secure-access) |
| **Categories** | domains |
| **First Published** | 2024-04-08 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **5 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`CategoryData`](../tables/categorydata.md) | Workbooks |
| [`NetworkAccessTraffic`](../tables/networkaccesstraffic.md) | Analytics, Workbooks |
| [`NetworkAccessTrafficData`](../tables/networkaccesstrafficdata.md) | Workbooks |
| [`NetworkData`](../tables/networkdata.md) | Workbooks |
| [`OfficeActivity`](../tables/officeactivity.md) | Workbooks |

## Content Items

This solution includes **6 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [GSA - Detect Abnormal Deny Rate for Source to Destination IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Analytic%20Rules/SWG%20-%20Abnormal%20Deny%20Rate.yaml) | Medium | InitialAccess, Exfiltration, CommandAndControl | [`NetworkAccessTraffic`](../tables/networkaccesstraffic.md) |
| [GSA - Detect Connections Outside Operational Hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Analytic%20Rules/Identity%20-%20AfterHoursActivity.yaml) | High | InitialAccess | [`NetworkAccessTraffic`](../tables/networkaccesstraffic.md) |
| [GSA - Detect Protocol Changes for Destination Ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Analytic%20Rules/SWG%20-%20Abnormal%20Port%20to%20Protocol.yaml) | Medium | DefenseEvasion, Exfiltration, CommandAndControl | [`NetworkAccessTraffic`](../tables/networkaccesstraffic.md) |
| [GSA - Detect Source IP Scanning Multiple Open Ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Analytic%20Rules/SWG%20-%20Source%20IP%20Port%20Scan.yaml) | Medium | Discovery | [`NetworkAccessTraffic`](../tables/networkaccesstraffic.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [GSAM365EnrichedEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Workbooks/GSAM365EnrichedEvents.json) | [`NetworkAccessTraffic`](../tables/networkaccesstraffic.md)<br>[`OfficeActivity`](../tables/officeactivity.md) |
| [GSANetworkTraffic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Workbooks/GSANetworkTraffic.json) | [`CategoryData`](../tables/categorydata.md)<br>[`NetworkAccessTraffic`](../tables/networkaccesstraffic.md)<br>[`NetworkAccessTrafficData`](../tables/networkaccesstrafficdata.md)<br>[`NetworkData`](../tables/networkdata.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                       |
|-------------|--------------------------------|------------------------------------------------------------------------------------------|
| 3.0.1       | 16-09-2025                     | Made an update to the logic of the Abnormal Port-to-Protocol **Analytic Rule** |
| 3.0.0       | 01-08-2025                     | Updates to the workbook to improve the clarity and consistency of titles for visualizations |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
