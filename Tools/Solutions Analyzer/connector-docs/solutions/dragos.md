# Dragos

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Dragos Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://www.dragos.com](https://www.dragos.com) |
| **Categories** | domains |
| **First Published** | 2025-01-23 |
| **Last Updated** | 2025-01-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [ Dragos Notifications via Cloud Sitestore](../connectors/dragossitestoreccp.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`DragosAlerts_CL`](../tables/dragosalerts-cl.md) | [ Dragos Notifications via Cloud Sitestore](../connectors/dragossitestoreccp.md) | - |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | - | Analytics |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 4 |
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Dragos Notifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos/Analytic%20Rules/DragosNotifiction.yaml) | Medium | - | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [DragosNotificationsToSentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos/Parsers/DragosNotificationsToSentinel.yaml) | - | - |
| [DragosPullNotificationsToSentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos/Parsers/DragosPullNotificationsToSentinel.yaml) | - | - |
| [DragosPushNotificationsToSentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos/Parsers/DragosPushNotificationsToSentinel.yaml) | - | - |
| [DragosSeverityToSentinelSeverity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos/Parsers/DragosSeverityToSentinelSeverity.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.0       | 10-01-2025                     | Initial solution release.                      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
