# Okta Single Sign-On

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-03-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On) |

## Data Connectors

This solution provides **4 data connector(s)**:

- [Okta Single Sign-On](../connectors/oktasso.md)
- [Okta Single Sign-On (Polling CCP)](../connectors/oktasso-polling.md)
- [Okta Single Sign-On](../connectors/oktassov2.md)
- [Okta Single Sign-On (using Azure Functions)](../connectors/oktasinglesignon%28usingazurefunctions%29.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`OktaNativePoller_CL`](../tables/oktanativepoller-cl.md) | [Okta Single Sign-On (Polling CCP)](../connectors/oktasso-polling.md) | - |
| [`OktaV2_CL`](../tables/oktav2-cl.md) | [Okta Single Sign-On](../connectors/oktassov2.md), [Okta Single Sign-On (using Azure Functions)](../connectors/oktasinglesignon(usingazurefunctions).md) | Analytics, Hunting, Workbooks |
| [`Okta_CL`](../tables/okta-cl.md) | [Okta Single Sign-On](../connectors/oktasso.md), [Okta Single Sign-On](../connectors/oktassov2.md), [Okta Single Sign-On (using Azure Functions)](../connectors/oktasinglesignon(usingazurefunctions).md) | Analytics, Hunting, Workbooks |
| [`signIns`](../tables/signins.md) | [Okta Single Sign-On (Preview)](../connectors/oktassov2.md), [Okta Single Sign-On (using Azure Functions)](../connectors/oktasinglesignon(usingazurefunctions).md) | Hunting |

## Content Items

This solution includes **24 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 10 |
| Analytic Rules | 9 |
| Playbooks | 3 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Device Registration from Malicious IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Analytic%20Rules/DeviceRegistrationMaliciousIP.yaml) | High | Persistence | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [Failed Logins from Unknown or Invalid User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Analytic%20Rules/FailedLoginsFromUnknownOrInvalidUser.yaml) | Medium | CredentialAccess | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [High-Risk Admin Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Analytic%20Rules/HighRiskAdminActivity.yaml) | Medium | Persistence | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [MFA Fatigue (OKTA)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Analytic%20Rules/MFAFatigue.yaml) | Medium | CredentialAccess | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [New Device/Location sign-in along with critical operation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Analytic%20Rules/NewDeviceLocationCriticalOperation.yaml) | Medium | InitialAccess, Persistence | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [Okta Fast Pass phishing Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Analytic%20Rules/PhishingDetection.yaml) | Medium | InitialAccess | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [Potential Password Spray Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Analytic%20Rules/PasswordSpray.yaml) | Medium | CredentialAccess | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [User Login from Different Countries within 3 hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Analytic%20Rules/LoginfromUsersfromDifferentCountrieswithin3hours.yaml) | High | InitialAccess | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [User Session Impersonation(Okta)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Analytic%20Rules/UserSessionImpersonation.yaml) | Medium | PrivilegeEscalation | [`Okta_CL`](../tables/okta-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Admin privilege granted (Okta)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Hunting%20Queries/AdminPrivilegeGrant.yaml) | Persistence | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [Create API Token (Okta)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Hunting%20Queries/CreateAPIToken.yaml) | PrivilegeEscalation | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [Initiate impersonation session (Okta)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Hunting%20Queries/ImpersonationSession.yaml) | InitialAccess | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [Logins originating from VPS Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Hunting%20Queries/LoginsVPSProvider.yaml) | InitialAccess | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [New device registration from unfamiliar location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Hunting%20Queries/NewDeviceRegistration.yaml) | Persistence | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [Okta Login from multiple locations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Hunting%20Queries/LoginFromMultipleLocations.yaml) | CredentialAccess | [`signIns`](../tables/signins.md) |
| [Okta login attempts using Legacy Auth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Hunting%20Queries/LegacyAuthentication.yaml) | CredentialAccess | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [Rare MFA Operations (Okta)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Hunting%20Queries/RareMFAOperation.yaml) | Persistence | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [Sign-ins from Nord VPN Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Hunting%20Queries/LoginNordVPN.yaml) | InitialAccess | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |
| [User password reset(Okta)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Hunting%20Queries/UserPasswordReset.yaml) | Persistence | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [OktaSingleSignOn](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Workbooks/OktaSingleSignOn.json) | [`OktaV2_CL`](../tables/oktav2-cl.md)<br>[`Okta_CL`](../tables/okta-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Prompt Okta user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Playbooks/OktaPlaybooks/Okta-PromptUser/azuredeploy.json) | This playbook uses the OKTA connector to prompt the risky user on Teams. User is asked action was ta... | - |
| [Response on Okta user from Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Playbooks/OktaPlaybooks/Okta-ResponseFromTeams/azuredeploy.json) | This playbooks sends an adaptive card to the SOC Teams channel with information about the Okta user ... | - |
| [User enrichment - Okta](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Playbooks/OktaPlaybooks/Okta-EnrichIncidentWithUserDetails/azuredeploy.json) | This playbook will collect user information from Okta and post a report on the incident. | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [OktaSSO](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Parsers/OktaSSO.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                            |
|-------------|--------------------------------|---------------------------------------------------------------|
| 3.1.2       | 06-01-2025                     | Removing Custom Entity mappings from **Analytic Rule**                         |
| 3.1.1       | 08-11-2024                     | Fixed CCP **Data Connector** connection bug                          |
| 3.1.0       | 27-11-2024                     | Fixed Solution version in Maintemplate and resolved ARM template error                           |
| 3.0.10      | 08-11-2024                     | Updated **Parser** to fix the schema                          |
| 3.0.9       | 17-10-2024                     | Updated package to fix connectivity of CCP connector |
| 3.0.8       | 14-08-2024                     | Data Connector Globally Available         |
| 3.0.7       | 25-04-2024                     | Repackaged for parser issue with old names       |
| 3.0.6       | 17-04-2024                     | Repackaged solution for parser fix   |
| 3.0.5       | 08-04-2024                     | Added Azure Deploy button for government portal deployments   |
| 3.0.4       | 18-03-2024                     | Updated description in data file, data connector and added logo for ccp data connector                    |
| 3.0.3       | 08-03-2024                     | Updated ccp with domainname in dcr, tables, name change in definition and poller                     |
| 3.0.2       | 20-02-2024                     | Updated _solutionVersion to resource specific version and repackage                    |
| 3.0.1       | 24-01-2024                     | New **Analytic Rule** added (UserSessionImpersonation.yaml)  |
| 3.0.0       | 10-10-2023                     | Manual deployment instructions updated for **Data Connector** |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
