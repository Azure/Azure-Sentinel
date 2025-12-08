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

[← Back to Connectors Index](../connectors-index.md)
