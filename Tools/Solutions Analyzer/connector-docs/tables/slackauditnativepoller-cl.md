# SlackAuditNativePoller_CL

## Solutions (1)

This table is used by the following solutions:

- [SlackAudit](../solutions/slackaudit.md)

## Connectors (2)

This table is ingested by the following connectors:

- [Slack](../connectors/slackaudit.md)
- [[DEPRECATED] Slack Audit](../connectors/slackauditapi.md)

---

## Content Items Using This Table (20)

### Analytic Rules (9)

**In solution [SlackAudit](../solutions/slackaudit.md):**
- [SlackAudit - Empty User Agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditEmptyUA.yaml)
- [SlackAudit - Multiple archived files uploaded in short period of time](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditMultipleArchivedFilesUploadedInShortTimePeriod.yaml)
- [SlackAudit - Multiple failed logins for user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditMultipleFailedLoginsForUser.yaml)
- [SlackAudit - Public link created for file which can contain sensitive information.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditSensitiveFile.yaml)
- [SlackAudit - Suspicious file downloaded.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditSuspiciousFileDownloaded.yaml)
- [SlackAudit - Unknown User Agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditUnknownUA.yaml)
- [SlackAudit - User email linked to account changed.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditUserEmailChanged.yaml)
- [SlackAudit - User login after deactivated.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditUserLoginAfterDeactivated.yaml)
- [SlackAudit - User role changed to admin or owner](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Analytic%20Rules/SlackAuditUserChangedToAdminOrOwner.yaml)

### Hunting Queries (10)

**In solution [SlackAudit](../solutions/slackaudit.md):**
- [SlackAudit - Applications installed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditApplicationsInstalled.yaml)
- [SlackAudit - Deactivated users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditDeactivatedUsers.yaml)
- [SlackAudit - Downloaded files stats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditDownloadedFilesByUser.yaml)
- [SlackAudit - Failed logins with unknown username](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditFailedLoginsUnknownUsername.yaml)
- [SlackAudit - New User created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditNewUsers.yaml)
- [SlackAudit - Suspicious files downloaded](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditSuspiciousFilesDownloaded.yaml)
- [SlackAudit - Uploaded files stats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditUploadedFilesByUser.yaml)
- [SlackAudit - User Permission Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditUserPermissionsChanged.yaml)
- [SlackAudit - User logins by IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditUserLoginsByIP.yaml)
- [SlackAudit - Users joined channels without invites](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Hunting%20Queries/SlackAuditUsersJoinedChannelsWithoutInvites.yaml)

### Workbooks (1)

**In solution [SlackAudit](../solutions/slackaudit.md):**
- [SlackAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Workbooks/SlackAudit.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
