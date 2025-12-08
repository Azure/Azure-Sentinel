#  Atlassian Confluence Audit (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `ConfluenceAuditCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ConfluenceAuditLogs_CL`](../tables-index.md#confluenceauditlogs_cl) |
| **Used in Solutions** | [AtlassianConfluenceAudit](../solutions/atlassianconfluenceaudit.md) |
| **Connector Definition Files** | [AtlassianConfluenceAudit_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Data%20Connectors/AtlassianConfluenceAuditLogs_CCP/AtlassianConfluenceAudit_DataConnectorDefinition.json) |

The [Atlassian Confluence](https://www.atlassian.com/software/confluence) Audit data connector provides the capability to ingest [Confluence Audit Records](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[← Back to Connectors Index](../connectors-index.md)
