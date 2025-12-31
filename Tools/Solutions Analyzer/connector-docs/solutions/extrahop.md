# ExtraHop

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | ExtraHop Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.extrahop.com/customer-support](https://www.extrahop.com/customer-support) |
| **Categories** | domains |
| **First Published** | 2025-02-11 |
| **Last Updated** | 2025-06-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [ExtraHop Detections Data Connector](../connectors/extrahop.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ExtraHop_Detections_CL`](../tables/extrahop-detections-cl.md) | [ExtraHop Detections Data Connector](../connectors/extrahop.md) | Analytics, Workbooks |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | - | Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Generate alerts based on ExtraHop detections recommended for triage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop/Analytic%20Rules/ExtraHopSentinelAlerts.yaml) | Medium | Persistence | [`ExtraHop_Detections_CL`](../tables/extrahop-detections-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ExtraHopDetectionsOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop/Workbooks/ExtraHopDetectionsOverview.json) | [`ExtraHop_Detections_CL`](../tables/extrahop-detections-cl.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ExtraHopDetections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop/Parsers/ExtraHopDetections.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 04-06-2025                     | Updated **Parser** and **Workbook** to fix issue.    |
| 3.0.0       | 19-03-2025                     | Initial Solution Release.                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
