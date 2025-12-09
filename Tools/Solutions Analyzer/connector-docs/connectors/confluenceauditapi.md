# [Deprecated] Atlassian Confluence Audit

| | |
|----------|-------|
| **Connector ID** | `ConfluenceAuditAPI` |
| **Publisher** | Atlassian |
| **Tables Ingested** | [`Confluence_Audit_CL`](../tables-index.md#confluence_audit_cl) |
| **Used in Solutions** | [AtlassianConfluenceAudit](../solutions/atlassianconfluenceaudit.md) |
| **Connector Definition Files** | [ConfluenceAudit_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Data%20Connectors/AtlassianConfluenceAuditDataConnector/ConfluenceAudit_API_FunctionApp.json) |

The [Atlassian Confluence](https://www.atlassian.com/software/confluence) Audit data connector provides the capability to ingest [Confluence Audit Records](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
