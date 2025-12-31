# TenableAD

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** |  |
| **Support Tier** |  |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Tenable.ad](../connectors/tenable.ad.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) | [Tenable.ad](../connectors/tenable.ad.md) | Analytics, Workbooks |

## Content Items

This solution includes **15 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 12 |
| Workbooks | 2 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Tenable.ad Active Directory attacks pathways](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdADAttacksPathways.yaml) | Low | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad DCShadow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdDCShadow.yaml) | High | DefenseEvasion | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad DCSync](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdDCSync.yaml) | High | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad Golden Ticket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdGoldenTicket.yaml) | High | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad Indicators of Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdIndicatorsOfAttack.yaml) | Low | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad Indicators of Exposures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdIndicatorsOfExposures.yaml) | Low | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad LSASS Memory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdLSASSMemory.yaml) | High | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad Password Guessing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdPasswordGuessing.yaml) | High | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad Password Spraying](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdPasswordSpraying.yaml) | High | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad Password issues](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdPasswordIssues.yaml) | Low | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad privileged accounts issues](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdPrivilegedAccountIssues.yaml) | Low | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [Tenable.ad user accounts issues](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Analytic%20Rules/TenableAdUserAccountIssues.yaml) | Low | CredentialAccess | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [TenableAdIoA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Workbooks/TenableAdIoA.json) | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |
| [TenableAdIoE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Workbooks/TenableAdIoE.json) | [`Tenable_ad_CL`](../tables/tenable-ad-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [afad_parser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Parsers/afad_parser.yaml) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
