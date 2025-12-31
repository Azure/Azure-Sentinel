# Alsid For AD

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Alsid |
| **Support Tier** | Partner |
| **Support Link** | [https://www.alsid.com/contact-us/](https://www.alsid.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Alsid for Active Directory](../connectors/alsidforad.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AlsidForADLog_CL`](../tables/alsidforadlog-cl.md) | [Alsid for Active Directory](../connectors/alsidforad.md) | - |

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
| [Alsid Active Directory attacks pathways](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/ADAttacksPathways.yaml) | Low | CredentialAccess | - |
| [Alsid DCShadow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/DCShadow.yaml) | High | DefenseEvasion | - |
| [Alsid DCSync](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/DCSync.yaml) | High | CredentialAccess | - |
| [Alsid Golden Ticket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/GoldenTicket.yaml) | High | CredentialAccess | - |
| [Alsid Indicators of Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/IndicatorsOfAttack.yaml) | Low | CredentialAccess | - |
| [Alsid Indicators of Exposures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/IndicatorsOfExposures.yaml) | Low | CredentialAccess | - |
| [Alsid LSASS Memory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/LSASSMemory.yaml) | High | CredentialAccess | - |
| [Alsid Password Guessing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/PasswordGuessing.yaml) | High | CredentialAccess | - |
| [Alsid Password Spraying](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/PasswordSpraying.yaml) | High | CredentialAccess | - |
| [Alsid Password issues](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/PasswordIssues.yaml) | Low | CredentialAccess | - |
| [Alsid privileged accounts issues](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/PrivilegedAccountIssues.yaml) | Low | CredentialAccess | - |
| [Alsid user accounts issues](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Analytic%20Rules/UserAccountIssues.yaml) | Low | CredentialAccess | - |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AlsidIoA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Workbooks/AlsidIoA.json) | - |
| [AlsidIoE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Workbooks/AlsidIoE.json) | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [afad_parser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Parsers/afad_parser.yaml) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
