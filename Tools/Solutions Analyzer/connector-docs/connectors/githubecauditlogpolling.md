# [Deprecated] GitHub Enterprise Audit Log

| | |
|----------|-------|
| **Connector ID** | `GitHubEcAuditLogPolling` |
| **Publisher** | GitHub |
| **Tables Ingested** | [`GitHubAuditLogPolling_CL`](../tables-index.md#githubauditlogpolling_cl) |
| **Used in Solutions** | [GitHub](../solutions/github.md) |
| **Connector Definition Files** | [azuredeploy_GitHub_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Data%20Connectors/azuredeploy_GitHub_native_poller_connector.json) |

The GitHub audit log connector provides the capability to ingest GitHub logs into Microsoft Sentinel. By connecting GitHub audit logs into Microsoft Sentinel, you can view this data in workbooks, use it to create custom alerts, and improve your investigation process. 



 **Note:** If you intended to ingest GitHub subscribed events into Microsoft Sentinel, please refer to GitHub (using Webhooks) Connector from "**Data Connectors**" gallery.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **GitHub API personal access token**: You need a GitHub personal access token to enable polling for the organization audit log. You may use either a classic token with 'read:org' scope OR a fine-grained token with 'Administration: Read-only' scope.
- **GitHub Enterprise type**: This connector will only function with GitHub Enterprise Cloud; it will not support GitHub Enterprise Server.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect the GitHub Enterprise Organization-level Audit Log to Microsoft Sentinel**

Enable GitHub audit logs. 
 Follow [this guide](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token) to create or find your personal access token.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
