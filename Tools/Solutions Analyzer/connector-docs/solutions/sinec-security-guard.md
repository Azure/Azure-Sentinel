# SINEC Security Guard

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Siemens AG |
| **Support Tier** | Partner |
| **Support Link** | [https://siemens.com/sinec-security-guard](https://siemens.com/sinec-security-guard) |
| **Categories** | domains,verticals |
| **First Published** | 2024-07-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SINEC%20Security%20Guard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SINEC%20Security%20Guard) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [SINEC Security Guard](../connectors/ssg.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SINECSecurityGuard_CL`](../tables/sinecsecurityguard-cl.md) | [SINEC Security Guard](../connectors/ssg.md) | Analytics |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [SSG_Security_Incidents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SINEC%20Security%20Guard/Analytic%20Rules/SSG_Azure_Sentinel_analytic_rule.yaml) | HIGH | Impact | [`SINECSecurityGuard_CL`](../tables/sinecsecurityguard-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                |
|-------------|--------------------------------|-----------------------------------|
| 3.0.0       | 12-11-2024                     | Initial Solution Release          |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
