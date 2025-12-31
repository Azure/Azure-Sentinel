# HIPAA Compliance

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-10-08 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HIPAA%20Compliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HIPAA%20Compliance) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **3 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Workbooks |
| [`DeviceInfo`](../tables/deviceinfo.md) | Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | Workbooks |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`SecurityIncident`](../tables/securityincident.md) | Workbooks |
| [`watchlist`](../tables/watchlist.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [HIPAACompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HIPAA%20Compliance/Workbooks/HIPAACompliance.json) | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`DeviceInfo`](../tables/deviceinfo.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`SecurityIncident`](../tables/securityincident.md)<br>[`watchlist`](../tables/watchlist.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                               |
|-------------|--------------------------------|------------------------------------------------------------------|
|  3.0.0      |  22-10-2025                    | Initial Solution release 										  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
