# Cyfirma Brand Intelligence

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-03-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md)

## Tables Reference

This solution uses **5 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyfirmaBIDomainITAssetAlerts_CL`](../tables/cyfirmabidomainitassetalerts-cl.md) | [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md) | Analytics |
| [`CyfirmaBIExecutivePeopleAlerts_CL`](../tables/cyfirmabiexecutivepeoplealerts-cl.md) | [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md) | Analytics |
| [`CyfirmaBIMaliciousMobileAppsAlerts_CL`](../tables/cyfirmabimaliciousmobileappsalerts-cl.md) | [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md) | Analytics |
| [`CyfirmaBIProductSolutionAlerts_CL`](../tables/cyfirmabiproductsolutionalerts-cl.md) | [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md) | Analytics |
| [`CyfirmaBISocialHandlersAlerts_CL`](../tables/cyfirmabisocialhandlersalerts-cl.md) | [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md) | Analytics |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [CYFIRMA - Brand Intelligence - Domain Impersonation High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Analytic%20Rules/BIDomainImpersonationHighRule.yaml) | High | ResourceDevelopment, InitialAccess, CommandAndControl | [`CyfirmaBIDomainITAssetAlerts_CL`](../tables/cyfirmabidomainitassetalerts-cl.md) |
| [CYFIRMA - Brand Intelligence - Domain Impersonation Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Analytic%20Rules/BIDomainImpersonationMediumRule.yaml) | Medium | ResourceDevelopment, InitialAccess, CommandAndControl | [`CyfirmaBIDomainITAssetAlerts_CL`](../tables/cyfirmabidomainitassetalerts-cl.md) |
| [CYFIRMA - Brand Intelligence - Executive/People Impersonation High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Analytic%20Rules/BIExecutivePeopleImpersonationHighRule.yaml) | High | Reconnaissance, ResourceDevelopment, InitialAccess | [`CyfirmaBIExecutivePeopleAlerts_CL`](../tables/cyfirmabiexecutivepeoplealerts-cl.md) |
| [CYFIRMA - Brand Intelligence - Executive/People Impersonation Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Analytic%20Rules/BIExecutivePeopleImpersonationMediumRule.yaml) | Medium | Reconnaissance, ResourceDevelopment, InitialAccess | [`CyfirmaBIExecutivePeopleAlerts_CL`](../tables/cyfirmabiexecutivepeoplealerts-cl.md) |
| [CYFIRMA - Brand Intelligence - Malicious Mobile App High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Analytic%20Rules/BIMaliciousMobileAppHighRule.yaml) | High | ResourceDevelopment, Execution, DefenseEvasion, CredentialAccess, CommandAndControl | [`CyfirmaBIMaliciousMobileAppsAlerts_CL`](../tables/cyfirmabimaliciousmobileappsalerts-cl.md) |
| [CYFIRMA - Brand Intelligence - Malicious Mobile App Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Analytic%20Rules/BIMaliciousMobileAppMediumRule.yaml) | Medium | ResourceDevelopment, Execution, DefenseEvasion, CredentialAccess, CommandAndControl | [`CyfirmaBIMaliciousMobileAppsAlerts_CL`](../tables/cyfirmabimaliciousmobileappsalerts-cl.md) |
| [CYFIRMA - Brand Intelligence - Product/Solution High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Analytic%20Rules/BIProductSolutionHighRule.yaml) | High | ResourceDevelopment, InitialAccess | [`CyfirmaBIProductSolutionAlerts_CL`](../tables/cyfirmabiproductsolutionalerts-cl.md) |
| [CYFIRMA - Brand Intelligence - Product/Solution Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Analytic%20Rules/BIProductSolutionMediumRule.yaml) | Medium | ResourceDevelopment, InitialAccess | [`CyfirmaBIProductSolutionAlerts_CL`](../tables/cyfirmabiproductsolutionalerts-cl.md) |
| [CYFIRMA - Brand Intelligence - Social Media Handle Impersonation Detected High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Analytic%20Rules/BISocialMediaHandlerHighRule.yaml) | High | Reconnaissance, ResourceDevelopment, InitialAccess | [`CyfirmaBISocialHandlersAlerts_CL`](../tables/cyfirmabisocialhandlersalerts-cl.md) |
| [CYFIRMA - Brand Intelligence - Social Media Handle Impersonation Detected Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Analytic%20Rules/BISocialMediaHandlerMediumRule.yaml) | Medium | Reconnaissance, ResourceDevelopment, InitialAccess | [`CyfirmaBISocialHandlersAlerts_CL`](../tables/cyfirmabisocialhandlersalerts-cl.md) |

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
