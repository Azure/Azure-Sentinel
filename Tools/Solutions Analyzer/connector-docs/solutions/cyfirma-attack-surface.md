# Cyfirma Attack Surface

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-03-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md)

## Tables Reference

This solution uses **6 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyfirmaASCertificatesAlerts_CL`](../tables/cyfirmaascertificatesalerts-cl.md) | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) | Analytics |
| [`CyfirmaASCloudWeaknessAlerts_CL`](../tables/cyfirmaascloudweaknessalerts-cl.md) | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) | Analytics |
| [`CyfirmaASConfigurationAlerts_CL`](../tables/cyfirmaasconfigurationalerts-cl.md) | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) | Analytics |
| [`CyfirmaASDomainIPReputationAlerts_CL`](../tables/cyfirmaasdomainipreputationalerts-cl.md) | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) | Analytics |
| [`CyfirmaASDomainIPVulnerabilityAlerts_CL`](../tables/cyfirmaasdomainipvulnerabilityalerts-cl.md) | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) | Analytics |
| [`CyfirmaASOpenPortsAlerts_CL`](../tables/cyfirmaasopenportsalerts-cl.md) | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) | Analytics |

## Content Items

This solution includes **12 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 12 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [CYFIRMA - Attack Surface - Cloud Weakness High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASCloudWeaknessHighRule.yaml) | High | InitialAccess, Collection, Discovery, Exfiltration | [`CyfirmaASCloudWeaknessAlerts_CL`](../tables/cyfirmaascloudweaknessalerts-cl.md) |
| [CYFIRMA - Attack Surface - Cloud Weakness Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASCloudWeaknessMediumRule.yaml) | Medium | InitialAccess, Collection, Discovery, Exfiltration | [`CyfirmaASCloudWeaknessAlerts_CL`](../tables/cyfirmaascloudweaknessalerts-cl.md) |
| [CYFIRMA - Attack Surface - Configuration High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASConfigurationsHighRule.yaml) | High | InitialAccess, Discovery, Persistence, Execution, DefenseEvasion, CredentialAccess, Collection, Reconnaissance | [`CyfirmaASConfigurationAlerts_CL`](../tables/cyfirmaasconfigurationalerts-cl.md) |
| [CYFIRMA - Attack Surface - Configuration Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASConfigurationsMediumRule.yaml) | Medium | InitialAccess, Discovery, Persistence, Execution, DefenseEvasion, CredentialAccess, Collection, Reconnaissance | [`CyfirmaASConfigurationAlerts_CL`](../tables/cyfirmaasconfigurationalerts-cl.md) |
| [CYFIRMA - Attack Surface - Domain/IP Vulnerability Exposure High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASDomainIPVulnerabilitiesHighRule.yaml) | High | InitialAccess, Discovery, DefenseEvasion, Persistence, Execution, Impact, PrivilegeEscalation | [`CyfirmaASDomainIPVulnerabilityAlerts_CL`](../tables/cyfirmaasdomainipvulnerabilityalerts-cl.md) |
| [CYFIRMA - Attack Surface - Domain/IP Vulnerability Exposure Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASDomainIPVulnerabilitiesMediumRule.yaml) | Medium | InitialAccess, Discovery, DefenseEvasion, Persistence, Execution, Impact, PrivilegeEscalation | [`CyfirmaASDomainIPVulnerabilityAlerts_CL`](../tables/cyfirmaasdomainipvulnerabilityalerts-cl.md) |
| [CYFIRMA - Attack Surface - Malicious Domain/IP Reputation High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASDomainIPreputationsHighRule.yaml) | High | InitialAccess, CommandAndControl, Reconnaissance, Impact, DefenseEvasion, Exfiltration | [`CyfirmaASDomainIPReputationAlerts_CL`](../tables/cyfirmaasdomainipreputationalerts-cl.md) |
| [CYFIRMA - Attack Surface - Malicious Domain/IP Reputation Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASDomainIPreputationsMediumRule.yaml) | Medium | InitialAccess, CommandAndControl, Reconnaissance, Impact, DefenseEvasion, Exfiltration | [`CyfirmaASDomainIPReputationAlerts_CL`](../tables/cyfirmaasdomainipreputationalerts-cl.md) |
| [CYFIRMA - Attack Surface - Open Ports High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASOpenPortsHighRule.yaml) | High | InitialAccess, CommandAndControl, Discovery, DefenseEvasion, Persistence | [`CyfirmaASOpenPortsAlerts_CL`](../tables/cyfirmaasopenportsalerts-cl.md) |
| [CYFIRMA - Attack Surface - Open Ports Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASOpenPortsMediumRule.yaml) | Medium | InitialAccess, CommandAndControl, Discovery, DefenseEvasion, Persistence | [`CyfirmaASOpenPortsAlerts_CL`](../tables/cyfirmaasopenportsalerts-cl.md) |
| [CYFIRMA - Attack Surface - Weak Certificate Exposure - High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASCertificatesHighRule.yaml) | High | DefenseEvasion, ResourceDevelopment, Reconnaissance, InitialAccess, CredentialAccess | [`CyfirmaASCertificatesAlerts_CL`](../tables/cyfirmaascertificatesalerts-cl.md) |
| [CYFIRMA - Attack Surface - Weak Certificate Exposure - Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Analytic%20Rules/ASCertificatesMediumRule.yaml) | Medium | DefenseEvasion, ResourceDevelopment, Reconnaissance, InitialAccess, CredentialAccess | [`CyfirmaASCertificatesAlerts_CL`](../tables/cyfirmaascertificatesalerts-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                     |
|-------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.3       | 04-09-2025                     | Bugs fixes to **CCF Data Connector**.                                  |
| 3.0.2       | 24-07-2025                     | Minor changes and New analytics rules added to **CCF Data Connector**. |
| 3.0.1       | 17-06-2025                     | Minor changes to **CCF Data Connector**.                               |
| 3.0.0       | 14-04-2025                     | Initial Solution Release.                                              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
