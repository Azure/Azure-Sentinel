# EatonForeseer

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/EatonForeseer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/EatonForeseer) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`SecurityEvent`](../tables/securityevent.md) | Analytics, Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [EatonForeseer - Unauthorized Logins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/EatonForeseer/Analytic%20Rules/EatonUnautorizedLogins.yaml) | High | InitialAccess | [`SecurityEvent`](../tables/securityevent.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [EatonForeseerHealthAndAccess](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/EatonForeseer/Workbooks/EatonForeseerHealthAndAccess.json) | [`SecurityEvent`](../tables/securityevent.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
