# Cloud Identity Threat Protection Essentials

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-11-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **3 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AuditLogs`](../tables/auditlogs.md) | Analytics, Hunting |
| [`NewUserAddsUser`](../tables/newuseraddsuser.md) | Hunting |
| [`SigninLogs`](../tables/signinlogs.md) | Hunting |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`BehaviorAnalytics`](../tables/behavioranalytics.md) | Hunting |
| [`IdentityInfo`](../tables/identityinfo.md) | Hunting |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 8 |
| Analytic Rules | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Multi-Factor Authentication Disabled for a User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Analytic%20Rules/MFADisable.yaml) | Medium | CredentialAccess, Persistence | - |
| [New External User Granted Admin Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Analytic%20Rules/NewExtUserGrantedAdmin.yaml) | Medium | Persistence | [`AuditLogs`](../tables/auditlogs.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Application Granted EWS Permissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/ApplicationGrantedEWSPermissions.yaml) | Collection, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [Detect Disabled Account Sign-in Attempts by Account Name](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/DisabledAccountSigninAttempts.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Detect Disabled Account Sign-in Attempts by IP Address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/DisabledAccountSigninAttemptsByIP.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md) |
| [Interactive STS refresh token modifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/StsRefreshTokenModification.yaml) | CredentialAccess | [`AuditLogs`](../tables/auditlogs.md) |
| [Sign-ins From VPS Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/Signins-From-VPS-Providers.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Sign-ins from Nord VPN Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/Signins-from-NordVPN-Providers.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Suspicious Sign-ins to Privileged Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/SuspiciousSignintoPrivilegedAccount.yaml) | InitialAccess | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [User Granted Access and Grants Access to Other Users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/UserGrantedAccess_GrantsOthersAccess.yaml) | Persistence, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md)<br>[`NewUserAddsUser`](../tables/newuseraddsuser.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                         |
|-------------|--------------------------------|----------------------------------------------------------------------------|
| 3.0.3       | 28-02-2024                     | Removed usage of BlastRadius from **Hunting Queries**                      |
| 3.0.2       | 09-02-2024                     | Tagged for dependent solutions for deployment                              |
| 3.0.1       | 16-01-2024                     | Sub-techniques added for **Analytical Rules**   							|
| 3.0.0       | 07-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
