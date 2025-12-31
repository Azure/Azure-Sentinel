# Illusive Platform

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Illusive Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://illusive.com/support](https://illusive.com/support) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Illusive Platform via Legacy Agent](../connectors/illusiveattackmanagementsystem.md)
- [[Deprecated] Illusive Platform via AMA](../connectors/illusiveattackmanagementsystemama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Illusive Platform via AMA](../connectors/illusiveattackmanagementsystemama.md), [[Deprecated] Illusive Platform via Legacy Agent](../connectors/illusiveattackmanagementsystem.md) | Analytics |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 2 |
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Illusive Incidents Analytic Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform/Analytic%20Rules/Illusive_Detection_Query.yaml) | Medium | Persistence, PrivilegeEscalation, DefenseEvasion, CredentialAccess, LateralMovement | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [IllusiveADS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform/Workbooks/IllusiveADS.json) | - |
| [IllusiveASM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform/Workbooks/IllusiveASM.json) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 12-07-2024                     |    Deprecating data connector                                      |
| 3.0.0       | 13-09-2023                     |	Addition of new Illusive Platform AMA **Data Connector**        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
