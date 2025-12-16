# GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview)

| | |
|----------|-------|
| **Connector ID** | `GitHubAuditDefinitionV2` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`GitHubAuditLogsV2_CL`](../tables-index.md#githubauditlogsv2_cl) |
| **Used in Solutions** | [GitHub](../solutions/github.md) |
| **Connector Definition Files** | [GitHubAuditLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Data%20Connectors/GitHubAuditLogs_CCF/GitHubAuditLogs_ConnectorDefinition.json) |

The GitHub audit log connector provides the capability to ingest GitHub logs into Microsoft Sentinel. By connecting GitHub audit logs into Microsoft Sentinel, you can view this data in workbooks, use it to create custom alerts, and improve your investigation process. 



 **Note:** If you intended to ingest GitHub subscribed events into Microsoft Sentinel, please refer to GitHub (using Webhooks) Connector from "**Data Connectors**" gallery.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **GitHub API personal access token**: To enable polling for the Enterprise audit log, ensure the authenticated user is an Enterprise admin and has a GitHub personal access token (classic) with the `read:audit_log` scope.
- **GitHub Enterprise type**: This connector will only function with GitHub Enterprise Cloud; it will not support GitHub Enterprise Server.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect the GitHub Enterprise-level Audit Log to Microsoft Sentinel**

Enable GitHub audit logs. 
 Follow [this guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) to create or find your personal access token.
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Github Enterprise API URL**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add Enterprise**

When you click the "Add Enterprise" button in the portal, a configuration form will open. You'll need to provide:

Enter your Github Enterprise API URL and API key. Github Enterprise API URL formats:
* `https://api.github.com/enterprises/{enterprise}`
* `https://api.{subdomain}.ghe.com/enterprises/{enterprise}`

- **Github Enterprise API URL** (optional): Your Github Enterprise API URL
- **API Key** (optional): Enter API Key

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
