# [DEPRECATED] Cloudflare

| | |
|----------|-------|
| **Connector ID** | `CloudflareDataConnector` |
| **Publisher** | Cloudflare |
| **Tables Ingested** | [`Cloudflare_CL`](../tables-index.md#cloudflare_cl) |
| **Used in Solutions** | [Cloudflare](../solutions/cloudflare.md) |
| **Connector Definition Files** | [Cloudflare_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Data%20Connectors/Cloudflare_API_FunctionApp.json) |

The Cloudflare data connector provides the capability to ingest [Cloudflare logs](https://developers.cloudflare.com/logs/) into Microsoft Sentinel using the Cloudflare Logpush and Azure Blob Storage. Refer to [Cloudflare  documentation](https://developers.cloudflare.com/logs/logpush) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
