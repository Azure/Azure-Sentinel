# [DEPRECATED] Slack Audit

| | |
|----------|-------|
| **Connector ID** | `SlackAuditAPI` |
| **Publisher** | Slack |
| **Tables Ingested** | [`SlackAudit_CL`](../tables-index.md#slackaudit_cl) |
| **Used in Solutions** | [SlackAudit](../solutions/slackaudit.md) |
| **Connector Definition Files** | [SlackAudit_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Data%20Connectors/SlackAudit_API_FunctionApp.json) |

The [Slack](https://slack.com) Audit data connector provides the capability to ingest [Slack Audit Records](https://api.slack.com/admins/audit-logs) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs#the_audit_event) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
