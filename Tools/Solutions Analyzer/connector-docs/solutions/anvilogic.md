# Anvilogic

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Anvilogic |
| **Support Tier** | Partner |
| **Support Link** | [https://www.anvilogic.com/](https://www.anvilogic.com/) |
| **Categories** | domains |
| **First Published** | 2025-06-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Anvilogic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Anvilogic) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Anvilogic](../connectors/anvilogicccfdefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Anvilogic_Alerts_CL`](../tables/anvilogic-alerts-cl.md) | [Anvilogic](../connectors/anvilogicccfdefinition.md) | Analytics |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Anvilogic Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Anvilogic/Analytic%20Rules/Anvilogic_Alerts.yaml) | Medium | - | [`Anvilogic_Alerts_CL`](../tables/anvilogic-alerts-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                           |
|-------------|--------------------------------|--------------------------------------------------------------|
| 3.0.0       | 20-06-2025                     | Initial Solution Release.                                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
