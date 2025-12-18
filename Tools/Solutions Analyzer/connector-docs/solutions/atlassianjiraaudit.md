# AtlassianJiraAudit

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Atlassian Jira Audit](../connectors/jiraauditapi.md)

**Publisher:** Atlassian

### [Atlassian Jira Audit (using REST API)](../connectors/jiraauditccpdefinition.md)

**Publisher:** Microsoft

The [Atlassian Jira](https://www.atlassian.com/software/jira) Audit data connector provides the capability to ingest [Jira Audit Records](https://support.atlassian.com/jira-cloud-administration/docs/audit-activities-in-jira-applications/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-audit-records/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Atlassian Jira API access**: Permission of [Administer Jira](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#authentication) is required to get access to the Jira Audit logs API. See [Jira API documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-audit-records/#api-group-audit-records) to learn more about the audit API.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

To enable the Atlassian Jira connector for Microsoft Sentinel, click to add an organization, fill the form with the Jira environment credentials and click to Connect. 
 Follow [these steps](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) to create an API token.
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Atlassian Jira organization URL**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add organization**

*Add Atlassian Jira organization*

When you click the "Add organization" button in the portal, a configuration form will open. You'll need to provide:

- **Atlassian Jira organization URL** (optional): Atlassian Jira organization URL
- **User Name** (optional): User Name (e.g., user@example.com)
- **API Key** (optional): API Key

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

| | |
|--------------------------|---|
| **Tables Ingested** | `Jira_Audit_v2_CL` |
| **Connector Definition Files** | [JiraAudit_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Data%20Connectors/JiraAuditAPISentinelConnector_ccpv2/JiraAudit_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/jiraauditccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Jira_Audit_CL` | [Atlassian Jira Audit](../connectors/jiraauditapi.md) |
| `Jira_Audit_v2_CL` | [Atlassian Jira Audit (using REST API)](../connectors/jiraauditccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
