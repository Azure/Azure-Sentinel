# GitLab

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-04-27 |
| **Last Updated** | 2022-06-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] GitLab](../connectors/gitlab.md)

## Tables Reference

This solution uses **6 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GitLabRepositoryDestroyEvents`](../tables/gitlabrepositorydestroyevents.md) | - | Analytics |
| [`SigninLogs`](../tables/signinlogs.md) | - | Analytics |
| [`Syslog`](../tables/syslog.md) | [[Deprecated] GitLab](../connectors/gitlab.md) | Analytics |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | - | Analytics |
| [`impersonationStart`](../tables/impersonationstart.md) | - | Analytics |
| [`true`](../tables/true.md) | - | Analytics |

## Content Items

This solution includes **12 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 9 |
| Parsers | 3 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [GitLab - Abnormal number of repositories deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_Repo_Deletion.yaml) | Medium | Impact | [`GitLabRepositoryDestroyEvents`](../tables/gitlabrepositorydestroyevents.md) |
| [GitLab - Brute-force Attempts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_BruteForce.yaml) | Medium | CredentialAccess | - |
| [GitLab - External User Added to GitLab](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_ExternalUser.yaml) | Medium | Persistence | [`Syslog`](../tables/syslog.md) |
| [GitLab - Local Auth - No MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_LocalAuthNoMFA.yaml) | Medium | CredentialAccess | [`Syslog`](../tables/syslog.md)<br>[`true`](../tables/true.md) |
| [GitLab - Personal Access Tokens creation over time](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_PAT_Repo.yaml) | Medium | Collection | [`Syslog`](../tables/syslog.md) |
| [GitLab - Repository visibility to Public](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_RepoVisibilityChange.yaml) | Medium | Persistence, DefenseEvasion, CredentialAccess | [`Syslog`](../tables/syslog.md) |
| [GitLab - SSO - Sign-Ins Burst](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_SignInBurst.yaml) | Medium | CredentialAccess | [`SigninLogs`](../tables/signinlogs.md) |
| [GitLab - TI - Connection from Malicious IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_MaliciousIP.yaml) | Medium | InitialAccess | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [GitLab - User Impersonation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_Impersonation.yaml) | Medium | Persistence | [`impersonationStart`](../tables/impersonationstart.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [GitLabAccess](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Parsers/GitLabAccess.yaml) | - | - |
| [GitLabApp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Parsers/GitLabApp.yaml) | - | - |
| [GitLabAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Parsers/GitLabAudit.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                        |
|-------------|--------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.2       | 12-12-2024                     | Removed Deprecated **Data connectors**                                                    |
| 3.0.1       | 07-24-2023                     | Deprecated data connectors                                                                |
| 3.0.0       | 07-11-2023                     | Modifying text as there is rebranding from Azure Active Directory to Microsoft Entra ID   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
