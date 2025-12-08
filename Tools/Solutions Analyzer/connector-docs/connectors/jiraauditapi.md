# Atlassian Jira Audit

| | |
|----------|-------|
| **Connector ID** | `JiraAuditAPI` |
| **Publisher** | Atlassian |
| **Tables Ingested** | [`Jira_Audit_CL`](../tables-index.md#jira_audit_cl) |
| **Used in Solutions** | [AtlassianJiraAudit](../solutions/atlassianjiraaudit.md) |
| **Connector Definition Files** | [JiraAudit_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Data%20Connectors/JiraAudit_API_FunctionApp.json) |

The [Atlassian Jira](https://www.atlassian.com/software/jira) Audit data connector provides the capability to ingest [Jira Audit Records](https://support.atlassian.com/jira-cloud-administration/docs/audit-activities-in-jira-applications/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-audit-records/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[← Back to Connectors Index](../connectors-index.md)
