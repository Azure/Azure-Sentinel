# [DEPRECATED] Google ApigeeX

| | |
|----------|-------|
| **Connector ID** | `ApigeeXDataConnector` |
| **Publisher** | Google |
| **Tables Ingested** | [`ApigeeX_CL`](../tables-index.md#apigeex_cl) |
| **Used in Solutions** | [Google Apigee](../solutions/google-apigee.md) |
| **Connector Definition Files** | [ApigeeX_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Apigee/Data%20Connectors/ApigeeX_FunctionApp.json) |

The [Google ApigeeX](https://cloud.google.com/apigee/docs) data connector provides the capability to ingest ApigeeX audit logs into Microsoft Sentinel using the GCP Logging API. Refer to [GCP Logging API documentation](https://cloud.google.com/logging/docs/reference/v2/rest) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
