# DORA Compliance

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-10-08 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DORA%20Compliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DORA%20Compliance) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **2 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) | Workbooks |
| [`Heartbeat`](../tables/heartbeat.md) | Workbooks |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | Workbooks |
| [`ThreatIntelIndicators`](../tables/threatintelindicators.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [DORACompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DORA%20Compliance/Workbooks/DORACompliance.json) | [`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`Heartbeat`](../tables/heartbeat.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                               |
|-------------|--------------------------------|------------------------------------------------------------------|
|  3.0.0      |  16-12-2025                    | Initial Solution release 										  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
