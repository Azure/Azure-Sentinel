# SenservaPro

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Senserva |
| **Support Tier** | Partner |
| **Support Link** | [https://www.senserva.com/contact/](https://www.senserva.com/contact/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [SenservaPro (Preview)](../connectors/senservapro.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SenservaProUnionQuery`](../tables/senservaprounionquery.md) | - | Workbooks |
| [`SenservaPro_CL`](../tables/senservapro-cl.md) | [SenservaPro (Preview)](../connectors/senservapro.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **33 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 15 |
| Hunting Queries | 15 |
| Workbooks | 3 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Azure Secure Score Self Service Password Reset](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/SelfServicePasswordReset.yaml) | High | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score MFA registration V2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/MFARegistration.yaml) | Medium | CredentialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score PW age policy new](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/PasswordAgePolicyNew.yaml) | Medium | CredentialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score admin MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/AdminMFA.yaml) | High | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score block legacy authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/BlockLegacyAuthentication.yaml) | High | CredentialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score one admin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/OneGlobalAdmin.yaml) | High | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score role overlap](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/GlobaAdminRoleOverlap.yaml) | Medium | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score sign in risk policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/SignInRiskPolicy.yaml) | Medium | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score user risk policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/UserRiskPolicy.yaml) | Medium | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Non-admin guest](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/NonAdminGuest.yaml) | Low | InitialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [SenservaPro AD Applications Not Using Client Credentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/AppsNoClientCredentials.yaml) | Medium | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Service principal not using client credentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/NotUsingClientCredentials.yaml) | High | InitialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Stale last password change](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/SearchStaleLastPasswordChange.yaml) | Low | InitialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Third party integrated apps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/ThirdPartyIntegratedApps.yaml) | High | Exfiltration | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [UserAccountDisabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Analytic%20Rules/UserAccountDisabled.yaml) | Medium | InitialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Application not using client credentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/ApplicationNotUsingClientCredentials.yaml) | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure Secure Score Self Service Password Reset](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/AzureSecureScoreSelfServicePasswordReset.yaml) | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score MFA registration V2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/AzureSecureScoreMFARegistrationV2.yaml) | CredentialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score PW age policy new](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/AzureSecureScorePWAgePolicyNew.yaml) | CredentialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score admin MFA V2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/AzureSecureScoreAdminMFAV2.yaml) | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score block legacy authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/AzureSecureScoreBlockLegacyAuthentication.yaml) | CredentialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score integrated apps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/AzureSecureScoreIntegratedApps.yaml) | Exfiltration | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score one admin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/AzureSecureScoreOneAdmin.yaml) | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score role overlap](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/AzureSecureScoreRoleOverlap.yaml) | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score sign in risk policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/AzureSecureScoreSigninRiskPolicy.yaml) | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Azure secure score user risk policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/AzureSecureScoreUserRiskPolicy.yaml) | Impact | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Non-admin guest](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/NonAdminGuest.yaml) | InitialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Service principal not using client credentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/ServicePrincipalNotUsingClientCredentials.yaml) | InitialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [Stale last password change](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/StaleLastPasswordChange.yaml) | InitialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [UserAccountDisabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Hunting%20Queries/UserAccountDisabled.yaml) | InitialAccess | [`SenservaPro_CL`](../tables/senservapro-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SenservaProAnalyticsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Workbooks/SenservaProAnalyticsWorkbook.json) | [`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [SenservaProMultipleWorkspaceWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Workbooks/SenservaProMultipleWorkspaceWorkbook.json) | [`SenservaProUnionQuery`](../tables/senservaprounionquery.md)<br>[`SenservaPro_CL`](../tables/senservapro-cl.md) |
| [SenservaProSecureScoreMultiTenantWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Workbooks/SenservaProSecureScoreMultiTenantWorkbook.json) | [`SenservaPro_CL`](../tables/senservapro-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.0       | 11-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
