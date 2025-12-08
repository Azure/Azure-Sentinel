# [DEPRECATED] Lookout

| | |
|----------|-------|
| **Connector ID** | `LookoutAPI` |
| **Publisher** | Lookout |
| **Tables Ingested** | [`Lookout_CL`](../tables-index.md#lookout_cl) |
| **Used in Solutions** | [Lookout](../solutions/lookout.md) |
| **Connector Definition Files** | [Lookout_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Data%20Connectors/Lookout_API_FunctionApp.json) |

The [Lookout](https://lookout.com) data connector provides the capability to ingest [Lookout](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide#commoneventfields) events into Microsoft Sentinel through the Mobile Risk API. Refer to [API documentation](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide) for more information. The [Lookout](https://lookout.com) data connector provides ability to get events which helps to examine potential security risks and more.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
