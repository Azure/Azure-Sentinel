# PCI DSS Compliance

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PCI%20DSS%20Compliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PCI%20DSS%20Compliance) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **3 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`Heartbeat`](../tables/heartbeat.md) | Workbooks |
| [`OracleDatabaseAuditEvent`](../tables/oracledatabaseauditevent.md) | Workbooks |
| [`SecurityEvent`](../tables/securityevent.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [PCIDSSCompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PCI%20DSS%20Compliance/Workbooks/PCIDSSCompliance.json) | [`Heartbeat`](../tables/heartbeat.md)<br>[`OracleDatabaseAuditEvent`](../tables/oracledatabaseauditevent.md)<br>[`SecurityEvent`](../tables/securityevent.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.0       | 16-10-2024                     |   Updated solution to fix content issue and data type for **Workbook** issue                                        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
