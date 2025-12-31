# Silverfort

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Silverfort |
| **Support Tier** | Partner |
| **Support Link** | [https://www.silverfort.com/customer-success/#support](https://www.silverfort.com/customer-success/#support) |
| **Categories** | domains |
| **First Published** | 2024-09-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Silverfort Admin Console](../connectors/silverfortama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [Silverfort Admin Console](../connectors/silverfortama.md) | Analytics, Workbooks |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Silverfort - Certifried Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Analytic%20Rules/Certifried.yaml) | High | PrivilegeEscalation | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Silverfort - Log4Shell Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Analytic%20Rules/Log4Shell.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Silverfort - NoPacBreach Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Analytic%20Rules/NoPac_Breach.yaml) | High | PrivilegeEscalation | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Silverfort - UserBruteForce Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Analytic%20Rules/User_Brute_Force.yaml) | High | CredentialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SilverfortWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Workbooks/SilverfortWorkbook.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                |
|-------------|--------------------------------|-----------------------------------|
| 3.0.0       | 13-09-2024                     | Initial Solution Release          |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
