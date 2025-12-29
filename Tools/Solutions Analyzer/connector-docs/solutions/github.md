# GitHub

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview)](../connectors/githubauditdefinitionv2.md)

**Publisher:** Microsoft

The GitHub audit log connector provides the capability to ingest GitHub logs into Microsoft Sentinel. By connecting GitHub audit logs into Microsoft Sentinel, you can view this data in workbooks, use it to create custom alerts, and improve your investigation process. 



 **Note:** If you intended to ingest GitHub subscribed events into Microsoft Sentinel, please refer to GitHub (using Webhooks) Connector from "**Data Connectors**" gallery.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GitHubAuditLogsV2_CL` |
| **Connector Definition Files** | [GitHubAuditLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Data%20Connectors/GitHubAuditLogs_CCF/GitHubAuditLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/githubauditdefinitionv2.md)

### [[Deprecated] GitHub Enterprise Audit Log](../connectors/githubecauditlogpolling.md)

**Publisher:** GitHub

The GitHub audit log connector provides the capability to ingest GitHub logs into Microsoft Sentinel. By connecting GitHub audit logs into Microsoft Sentinel, you can view this data in workbooks, use it to create custom alerts, and improve your investigation process. 



 **Note:** If you intended to ingest GitHub subscribed events into Microsoft Sentinel, please refer to GitHub (using Webhooks) Connector from "**Data Connectors**" gallery.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GitHubAuditLogPolling_CL` |
| **Connector Definition Files** | [azuredeploy_GitHub_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Data%20Connectors/azuredeploy_GitHub_native_poller_connector.json) |

[→ View full connector details](../connectors/githubecauditlogpolling.md)

### [GitHub (using Webhooks)](../connectors/githubwebhook.md)

**Publisher:** Microsoft

The [GitHub](https://www.github.com) webhook data connector provides the capability to ingest GitHub subscribed events into Microsoft Sentinel using [GitHub webhook events](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads). The connector provides ability to get events into Microsoft Sentinel which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more. 



 **Note:** If you are intended to ingest Github Audit logs, Please refer to GitHub Enterprise Audit Log Connector from "**Data Connectors**" gallery.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `githubscanaudit_CL` |
| **Connector Definition Files** | [GithubWebhook_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Data%20Connectors/GithubWebhook/GithubWebhook_API_FunctionApp.json) |

[→ View full connector details](../connectors/githubwebhook.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GitHubAuditLogPolling_CL` | [[Deprecated] GitHub Enterprise Audit Log](../connectors/githubecauditlogpolling.md) |
| `GitHubAuditLogsV2_CL` | [GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview)](../connectors/githubauditdefinitionv2.md) |
| `githubscanaudit_CL` | [GitHub (using Webhooks)](../connectors/githubwebhook.md) |

[← Back to Solutions Index](../solutions-index.md)
