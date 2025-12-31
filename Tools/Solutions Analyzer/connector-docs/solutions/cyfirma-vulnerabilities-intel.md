# Cyfirma Vulnerabilities Intel

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-05-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Vulnerabilities%20Intel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Vulnerabilities%20Intel) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CYFIRMA Vulnerabilities Intelligence](../connectors/cyfirmavulnerabilitiesinteldc.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyfirmaVulnerabilities_CL`](../tables/cyfirmavulnerabilities-cl.md) | [CYFIRMA Vulnerabilities Intelligence](../connectors/cyfirmavulnerabilitiesinteldc.md) | Analytics |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [CYFIRMA - High Severity Asset based Vulnerabilities Rule Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Vulnerabilities%20Intel/Analytic%20Rules/AssetVulnerabilitiesHighSeverityRule.yaml) | High | Execution, LateralMovement, PrivilegeEscalation, InitialAccess, CredentialAccess, DefenseEvasion | [`CyfirmaVulnerabilities_CL`](../tables/cyfirmavulnerabilities-cl.md) |
| [CYFIRMA - High Severity Attack Surface based Vulnerabilities Rule Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Vulnerabilities%20Intel/Analytic%20Rules/AttackSurfaceVulnerabilitiesHighSeverityRule.yaml) | High | Execution, LateralMovement, PrivilegeEscalation, InitialAccess, CredentialAccess, DefenseEvasion | [`CyfirmaVulnerabilities_CL`](../tables/cyfirmavulnerabilities-cl.md) |
| [CYFIRMA - Medium Severity Asset based Vulnerabilities Rule Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Vulnerabilities%20Intel/Analytic%20Rules/AssetVulnerabilitiesMediumSeverityRule.yaml) | Medium | Execution, LateralMovement, PrivilegeEscalation, InitialAccess, CredentialAccess, DefenseEvasion | [`CyfirmaVulnerabilities_CL`](../tables/cyfirmavulnerabilities-cl.md) |
| [CYFIRMA - Medium Severity Attack Surface based Vulnerabilities Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Vulnerabilities%20Intel/Analytic%20Rules/AttackSurfaceVulnerabilitiesMediumSeverityRule.yaml) | Medium | Execution, LateralMovement, PrivilegeEscalation, InitialAccess, CredentialAccess, DefenseEvasion | [`CyfirmaVulnerabilities_CL`](../tables/cyfirmavulnerabilities-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                     |
|-------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.2       | 04-09-2025                     | Bugs fixes to **CCF Data Connector**.                                  |
| 3.0.1       | 24-07-2025                     | Minor changes and New analytics rules added to **CCF Data Connector**. |
| 3.0.0       | 17-06-2025                     | Initial Solution Release.                                              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
