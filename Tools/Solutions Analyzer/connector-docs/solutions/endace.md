# Endace

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Endace |
| **Support Tier** | Partner |
| **Support Link** | [https://endace.com](https://endace.com) |
| **Categories** | domains |
| **First Published** | 2025-03-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endace) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Hunting |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 1 |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Endace - Pivot-to-Vision](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endace/Hunting%20Queries/Endace_Pivot-to-Vision.yaml) | ResourceDevelopment, InitialAccess, Discovery, LateralMovement, CommandandControl, Exfiltration | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                              |
|-------------|--------------------------------|-------------------------------------------------|
| 3.0.0       | 30-06-2025                     | Initial Release                                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
