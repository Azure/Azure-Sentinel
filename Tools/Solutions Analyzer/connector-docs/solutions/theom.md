# Theom

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Theom |
| **Support Tier** | Partner |
| **Support Link** | [https://www.theom.ai](https://www.theom.ai) |
| **Categories** | domains |
| **First Published** | 2022-11-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Theom](../connectors/theom.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`TheomAlerts_CL`](../tables/theomalerts-cl.md) | [Theom](../connectors/theom.md) | Analytics, Workbooks |

## Content Items

This solution includes **21 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 20 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Theom - Critical data in API headers or body](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0007-10_TRIS0014_Critical_data_in_API_headers_or_body.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Dark Data with large fin value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0032_Dark_Data_with_large_fin_value.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Dev secrets exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0012_Dev_secrets_exposed.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Dev secrets unencrypted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0001_Dev_secrets_unencrypted.yaml) | High | CredentialAccess | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Financial data exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0026_Financial_data_exposed.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Financial data unencrypted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0003_Financial_data_unencrypted.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Healthcare data exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0015_Healthcare_data_exposed.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Healthcare data unencrypted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0004_Healthcare_data_unencrypted.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Least priv large value shadow DB](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0033_Least_priv_large_value_shadow_DB.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - National IDs exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0018_National_IDs_exposed.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - National IDs unencrypted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0002_National_IDs_unencrypted.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Overprovisioned Roles Shadow DB](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0034_Overprovisioned_Roles_Shadow_DB.yaml) | High | Collection, PrivilegeEscalation | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Shadow DB large datastore value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0035_Shadow_DB_large_datastore_value.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Shadow DB with atypical accesses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0036_Shadow_DB_with_atypical_accesses.yaml) | High | Collection, PrivilegeEscalation | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom - Unencrypted public data stores](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TRIS0005_Unencrypted_public_data_stores.yaml) | High | Collection | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom Critical Risks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TheomRisksCritical.yaml) | High | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Exfiltration, Impact, Reconnaissance | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom High Risks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TheomRisksHigh.yaml) | High | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Exfiltration, Impact, Reconnaissance | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom Insights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TheomRisksInsights.yaml) | Low | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Exfiltration, Impact, Reconnaissance | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom Low Risks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TheomRisksLow.yaml) | High | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Exfiltration, Impact, Reconnaissance | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |
| [Theom Medium Risks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Analytic%20Rules/TheomRisksMedium.yaml) | High | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Exfiltration, Impact, Reconnaissance | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Theom](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Workbooks/Theom.json) | [`TheomAlerts_CL`](../tables/theomalerts-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       |     04-12-2023                 | Updated all **Analytical Rule**  with entity mappings     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
