# SlackAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-03-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit) |

## Data Connectors

This solution provides **3 data connector(s)**:

- [Slack](../connectors/slackaudit.md)
- [[DEPRECATED] Slack Audit](../connectors/slackauditapi.md)
- [SlackAudit (via Codeless Connector Framework)](../connectors/slackauditlogsccpdefinition.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md) | [Slack](../connectors/slackaudit.md), [[DEPRECATED] Slack Audit](../connectors/slackauditapi.md) | Analytics, Hunting, Workbooks |
| [`SlackAuditV2_CL`](../tables/slackauditv2-cl.md) | [SlackAudit (via Codeless Connector Framework)](../connectors/slackauditlogsccpdefinition.md), [[DEPRECATED] Slack Audit](../connectors/slackauditapi.md) | Analytics, Hunting, Workbooks |
| [`SlackAudit_CL`](../tables/slackaudit-cl.md) | [[DEPRECATED] Slack Audit](../connectors/slackauditapi.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **21 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 10 |
| Analytic Rules | 9 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [SlackAudit - Empty User Agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditEmptyUA.yaml) | Low | InitialAccess | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Multiple archived files uploaded in short period of time](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditMultipleArchivedFilesUploadedInShortTimePeriod.yaml) | Low | Exfiltration | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Multiple failed logins for user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditMultipleFailedLoginsForUser.yaml) | Medium | CredentialAccess | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Public link created for file which can contain sensitive information.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditSensitiveFile.yaml) | Medium | Exfiltration | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Suspicious file downloaded.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditSuspiciousFileDownloaded.yaml) | Medium | InitialAccess | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Unknown User Agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditUnknownUA.yaml) | Low | CommandAndControl | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - User email linked to account changed.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditUserEmailChanged.yaml) | Medium | InitialAccess | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - User login after deactivated.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditUserLoginAfterDeactivated.yaml) | Medium | InitialAccess, Persistence, PrivilegeEscalation | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - User role changed to admin or owner](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditUserChangedToAdminOrOwner.yaml) | Low | Persistence, PrivilegeEscalation | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [SlackAudit - Applications installed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditApplicationsInstalled.yaml) | InitialAccess | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Deactivated users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditDeactivatedUsers.yaml) | Impact | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Downloaded files stats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditDownloadedFilesByUser.yaml) | InitialAccess | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Failed logins with unknown username](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditFailedLoginsUnknownUsername.yaml) | CredentialAccess | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - New User created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditNewUsers.yaml) | Persistence | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Suspicious files downloaded](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditSuspiciousFilesDownloaded.yaml) | InitialAccess | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Uploaded files stats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditUploadedFilesByUser.yaml) | Exfiltration | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - User Permission Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditUserPermissionsChanged.yaml) | PrivilegeEscalation | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - User logins by IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditUserLoginsByIP.yaml) | InitialAccess, Persistence | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |
| [SlackAudit - Users joined channels without invites](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditUsersJoinedChannelsWithoutInvites.yaml) | InitialAccess, Persistence | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SlackAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Workbooks/SlackAudit.json) | [`SlackAuditNativePoller_CL`](../tables/slackauditnativepoller-cl.md)<br>[`SlackAuditV2_CL`](../tables/slackauditv2-cl.md)<br>[`SlackAudit_CL`](../tables/slackaudit-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SlackAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Parsers/SlackAudit.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.5       | 12-12-2025                     | Updated the **Parser** yaml file. |
| 3.0.4       | 28-07-2025                     | Removed Deprecated **Data Connector**. |
| 3.0.3       | 30-06-2025                     | Moving **CCF Data Connector** to GA. |
| 3.0.2       | 30-05-2025                     | Preview tag added to **CCF Data Connector**. |
| 3.0.1       | 24-04-2025                     | Migrated the **Function app Connector** to **CCP Data Connector** and Updated the **Parser**. |
| 3.0.0       | 23-08-2023                     | Manual deployment instructions updated for **Data Connector** & Convert **Parser** from text to yaml. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
