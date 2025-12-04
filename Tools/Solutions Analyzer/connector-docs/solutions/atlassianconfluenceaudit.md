# AtlassianConfluenceAudit

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit) |\n\n## Data Connectors

This solution provides **3 data connector(s)**.

### Atlassian Confluence

**Publisher:** Atlassian

The Atlassian Confluence data connector provides the capability to ingest [Atlassian Confluence audit logs](https://developer.atlassian.com/cloud/confluence/rest/api-group-audit/) into Microsoft Sentinel.

**Tables Ingested:**

- `AtlassianConfluenceNativePoller_CL`

**Connector Definition Files:**

- [azuredeploy_Confluence_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Data%20Connectors/ConfluenceNativePollerConnector/azuredeploy_Confluence_native_poller_connector.json)

### [Deprecated] Atlassian Confluence Audit

**Publisher:** Atlassian

The [Atlassian Confluence](https://www.atlassian.com/software/confluence) Audit data connector provides the capability to ingest [Confluence Audit Records](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

**Tables Ingested:**

- `Confluence_Audit_CL`

**Connector Definition Files:**

- [ConfluenceAudit_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Data%20Connectors/AtlassianConfluenceAuditDataConnector/ConfluenceAudit_API_FunctionApp.json)

###  Atlassian Confluence Audit (via Codeless Connector Framework)

**Publisher:** Microsoft

The [Atlassian Confluence](https://www.atlassian.com/software/confluence) Audit data connector provides the capability to ingest [Confluence Audit Records](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

**Tables Ingested:**

- `ConfluenceAuditLogs_CL`

**Connector Definition Files:**

- [AtlassianConfluenceAudit_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Data%20Connectors/AtlassianConfluenceAuditLogs_CCP/AtlassianConfluenceAudit_DataConnectorDefinition.json)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AtlassianConfluenceNativePoller_CL` | Atlassian Confluence |
| `ConfluenceAuditLogs_CL` | 1 connector(s) |
| `Confluence_Audit_CL` | [Deprecated] Atlassian Confluence Audit |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n