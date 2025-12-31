# GitHub

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub) |

## Data Connectors

This solution provides **3 data connector(s)**:

- [GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview)](../connectors/githubauditdefinitionv2.md)
- [[Deprecated] GitHub Enterprise Audit Log](../connectors/githubecauditlogpolling.md)
- [GitHub (using Webhooks)](../connectors/githubwebhook.md)

## Tables Reference

This solution uses **10 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GitHubActorLogin`](../tables/githubactorlogin.md) | - | Hunting |
| [`GitHubAudit`](../tables/githubaudit.md) | - | Analytics |
| [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md) | [[Deprecated] GitHub Enterprise Audit Log](../connectors/githubecauditlogpolling.md) | Analytics, Hunting |
| [`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) | [GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview)](../connectors/githubauditdefinitionv2.md), [[Deprecated] GitHub Enterprise Audit Log](../connectors/githubecauditlogpolling.md) | Analytics, Hunting |
| [`GitHubCountryCodeLogs`](../tables/githubcountrycodelogs.md) | - | Analytics |
| [`GitHubOrgMemberLogs`](../tables/githuborgmemberlogs.md) | - | Hunting |
| [`GitHubRepo`](../tables/githubrepo.md) | - | Analytics |
| [`GitHubRepositoryDestroyEvents`](../tables/githubrepositorydestroyevents.md) | - | Hunting |
| [`GitHubUser`](../tables/githubuser.md) | - | Hunting |
| [`githubscanaudit_CL`](../tables/githubscanaudit-cl.md) | [GitHub (using Webhooks)](../connectors/githubwebhook.md) | Workbooks |

## Content Items

This solution includes **28 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 14 |
| Hunting Queries | 8 |
| Parsers | 4 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [(Preview) GitHub - A payment method was removed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20A%20payment%20method%20was%20removed.yaml) | Medium | InitialAccess | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [(Preview) GitHub - Oauth application - a client secret was removed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20Oauth%20application%20-%20a%20client%20secret%20was%20removed.yaml) | Medium | InitialAccess | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [(Preview) GitHub - Repository was created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20Repository%20was%20created.yaml) | Medium | InitialAccess | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [(Preview) GitHub - Repository was destroyed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20Repository%20was%20destroyed.yaml) | Medium | InitialAccess | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [(Preview) GitHub - User visibility Was changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20User%20visibility%20Was%20changed.yaml) | Medium | InitialAccess | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [(Preview) GitHub - User was added to the organization](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20User%20was%20added%20to%20the%20organization.yaml) | Medium | InitialAccess | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [(Preview) GitHub - User was blocked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20User%20was%20blocked.yaml) | Medium | InitialAccess | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [(Preview) GitHub - User was invited to the repository](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20User%20was%20invited%20to%20the%20repository.yaml) | Medium | InitialAccess | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [(Preview) GitHub - pull request was created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20pull%20request%20was%20created.yaml) | Medium | InitialAccess | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [(Preview) GitHub - pull request was merged](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20pull%20request%20was%20merged.yaml) | Medium | InitialAccess | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [GitHub Activites from a New Country](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20Activities%20from%20Infrequent%20Country.yaml) | Medium | InitialAccess | [`GitHubCountryCodeLogs`](../tables/githubcountrycodelogs.md) |
| [GitHub Security Vulnerability in Repository](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/Security%20Vulnerability%20in%20Repo.yaml) | Informational | InitialAccess, Execution, PrivilegeEscalation, DefenseEvasion, CredentialAccess, LateralMovement | [`GitHubRepo`](../tables/githubrepo.md) |
| [GitHub Two Factor Auth Disable](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/%28Preview%29%20GitHub%20-%20Two%20Factor%20Authentication%20Disabled%20in%20GitHub.yaml) | Medium | DefenseEvasion | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [NRT GitHub Two Factor Auth Disable](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Analytic%20Rules/NRT%20Two%20Factor%20Authentication%20Disabled.yaml) | Medium | DefenseEvasion | [`GitHubAudit`](../tables/githubaudit.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [GitHub First Time Invite Member and Add Member to Repo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Hunting%20Queries/First%20Time%20User%20Invite%20and%20Add%20Member%20to%20Org.yaml) | Persistence | [`GitHubOrgMemberLogs`](../tables/githuborgmemberlogs.md) |
| [GitHub First Time Repo Delete](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Hunting%20Queries/User%20First%20Time%20Repository%20Delete%20Activity.yaml) | Impact | [`GitHubRepositoryDestroyEvents`](../tables/githubrepositorydestroyevents.md) |
| [GitHub Inactive or New Account Access or Usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Hunting%20Queries/Inactive%20or%20New%20Account%20Usage.yaml) | Persistence | [`GitHubActorLogin`](../tables/githubactorlogin.md)<br>[`GitHubUser`](../tables/githubuser.md) |
| [GitHub Mass Deletion of repos or projects](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Hunting%20Queries/Mass%20Deletion%20of%20Repositories%20.yaml) | Impact | [`GitHubRepositoryDestroyEvents`](../tables/githubrepositorydestroyevents.md) |
| [GitHub OAuth App Restrictions Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Hunting%20Queries/Oauth%20App%20Restrictions%20Disabled.yaml) | Persistence, DefenseEvasion | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [GitHub Repo switched from private to public](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Hunting%20Queries/Repository%20Permission%20Switched%20to%20Public.yaml) | Collection | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [GitHub Update Permissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Hunting%20Queries/Org%20Repositories%20Default%20Permissions%20Change.yaml) | Persistence, DefenseEvasion | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |
| [GitHub User Grants Access and Other User Grants Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Hunting%20Queries/User%20Grant%20Access%20and%20Grants%20Other%20Access.yaml) | Persistence, PrivilegeEscalation | [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`GitHubAuditLogsV2_CL`](../tables/githubauditlogsv2-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [GitHub](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Workbooks/GitHub.json) | [`githubscanaudit_CL`](../tables/githubscanaudit-cl.md) |
| [GitHubAdvancedSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Workbooks/GitHubAdvancedSecurity.json) | [`githubscanaudit_CL`](../tables/githubscanaudit-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [GitHubAuditData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Parsers/GitHubAuditData.yaml) | - | - |
| [GitHubCodeScanningData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Parsers/GitHubCodeScanningData.yaml) | - | - |
| [GitHubDependabotData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Parsers/GitHubDependabotData.yaml) | - | - |
| [GitHubSecretScanningData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Parsers/GitHubSecretScanningData.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.1.2       | 24-11-2025                     | Added clarity to Github Enterprise Audit CCF connector definition to use API URL. |
| 3.1.1       | 13-11-2025                     | Fixed URL handling for GitHub Enterprise Audit CCF connector.|
| 3.1.0       | 05-11-2025                     | Updated Github Enterprise Audit CCF connector to use full URL instead of enterprise name. |
| 3.0.9       | 05-09-2025                     | Enhancements to user guidance for connecting GitHub Enterprise audit logs connector                      |
| 3.0.8       | 26-08-2025                     | Removed deprecated tag from webhook connector.                      |
| 3.0.7       | 19-06-2025                     | Introducing a new CCF-based GitHub Enterprise Audit connector to replace the CLV1 connector                      |
| 3.0.6       | 26-04-2024                     | Repackaged for fix on parser in maintemplate to have old parsername and parentid.                    |
| 3.0.5       | 18-04-2024                     | Repackaged to fix parser issue.                                                  |
| 3.0.4       | 04-04-2024                     | Updated Entity Mappings in **Analytic Rules**.                                                 |
| 3.0.3       | 31-01-2024                     | Updated the solution to fix **Analytic Rules** deployment issue.              |
| 3.0.2       | 06-11-2023                     | Updated the **Workbook** name to resolve the issue of multiple keywords.  |
| 3.0.1       | 22-08-2023                     | Modified **GitHubWorkbook** to add new features (a.Filtering by organizations, b.Filtering by repository topics).  |
| 3.0.0       | 17-07-2023                     | **Data Connectors** description updated & Code Enhancements added for **Workbooks**. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
