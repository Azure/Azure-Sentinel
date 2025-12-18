# SlackAudit

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-03-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [Slack](../connectors/slackaudit.md)

**Publisher:** Slack

### [[DEPRECATED] Slack Audit](../connectors/slackauditapi.md)

**Publisher:** Slack

### [SlackAudit (via Codeless Connector Framework)](../connectors/slackauditlogsccpdefinition.md)

**Publisher:** Microsoft

The SlackAudit data connector provides the capability to ingest [Slack Audit logs](https://api.slack.com/admins/audit-logs) into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs-call) for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **UserName, SlackAudit API Key & Action Type**: To Generate the Access Token, create a new application in Slack, then add necessary scopes and configure the redirect URL. For detailed instructions on generating the access token, user name and action name limit, refer the [link](https://github.com/v-gsrihitha/v-gsrihitha/blob/main/SlackAudit/Readme.md).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect SlackAudit to Microsoft Sentinel**

To ingest data from SlackAudit to Microsoft Sentinel, you have to click on Add Domain button below then you get a pop up to fill the details, provide the required information and click on Connect. You can see the usernames, actions connected in the grid.
>
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **UserName**
- **Actions**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add domain**

*Add domain*

When you click the "Add domain" button in the portal, a configuration form will open. You'll need to provide:

- **UserName** (optional): Enter your User Name
- **SlackAudit API Key** (optional): Enter your API KEY
- **SlackAudit Action Type** (optional): Enter the Action Type

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

| | |
|--------------------------|---|
| **Tables Ingested** | `SlackAuditV2_CL` |
| **Connector Definition Files** | [SlackAuditLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Data%20Connectors/SlackAuditLog_CCP/SlackAuditLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/slackauditlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SlackAuditNativePoller_CL` | [Slack](../connectors/slackaudit.md) |
| `SlackAuditV2_CL` | [SlackAudit (via Codeless Connector Framework)](../connectors/slackauditlogsccpdefinition.md) |
| `SlackAudit_CL` | [[DEPRECATED] Slack Audit](../connectors/slackauditapi.md) |

[← Back to Solutions Index](../solutions-index.md)
