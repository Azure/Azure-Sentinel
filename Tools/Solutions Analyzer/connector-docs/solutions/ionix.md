# IONIX

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | IONIX |
| **Support Tier** | Partner |
| **Support Link** | [https://www.ionix.io/contact-us/](https://www.ionix.io/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [IONIX Security Logs](../connectors/cyberpionsecuritylogs.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyberpionActionItems_CL`](../tables/cyberpionactionitems-cl.md) | [IONIX Security Logs](../connectors/cyberpionsecuritylogs.md) | Analytics, Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [High Urgency IONIX Action Items](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX/Analytic%20Rules/HighUrgencyActionItems.yaml) | High | InitialAccess | [`CyberpionActionItems_CL`](../tables/cyberpionactionitems-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [IONIXOverviewWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX/Workbooks/IONIXOverviewWorkbook.json) | [`CyberpionActionItems_CL`](../tables/cyberpionactionitems-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------------------------------------------------------|
| 3.0.0       | 20-09-2023                     | 	A UI-only update as part of a re-branding from "Cyberpion" to "IONIX" (no change to core functionality) \| v1.0.1 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
