#  Atlassian Confluence Audit (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `ConfluenceAuditCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ConfluenceAuditLogs_CL`](../tables-index.md#confluenceauditlogs_cl) |
| **Used in Solutions** | [AtlassianConfluenceAudit](../solutions/atlassianconfluenceaudit.md) |
| **Connector Definition Files** | [AtlassianConfluenceAudit_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Data%20Connectors/AtlassianConfluenceAuditLogs_CCP/AtlassianConfluenceAudit_DataConnectorDefinition.json) |

The [Atlassian Confluence](https://www.atlassian.com/software/confluence) Audit data connector provides the capability to ingest [Confluence Audit Records](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Atlassian Confluence API access**: Permission of [Administer Confluence](https://developer.atlassian.com/cloud/confluence/rest/v1/intro/#auth) is required to get access to the Confluence Audit logs API. See [Confluence API documentation](https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-audit/#api-wiki-rest-api-audit-get) to learn more about the audit API.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

To enable the Atlassian Confluence connector for Microsoft Sentinel, click to add an organization, fill the form with the Confluence environment credentials and click to Connect. 
 Follow [these steps](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) to create an API token.
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Atlassian Confluence organization URL**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add organization**

*Add Atlassian Confluence organization*

When you click the "Add organization" button in the portal, a configuration form will open. You'll need to provide:

- **Atlassian Confluence organization URL** (optional): <your-domain>.atlassian.net
- **User Name** (optional): User Name (e.g., user@example.com)
- **API Token** (optional): API Token

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
