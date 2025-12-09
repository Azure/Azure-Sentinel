# [DEPRECATED] Salesforce Service Cloud

| | |
|----------|-------|
| **Connector ID** | `SalesforceServiceCloud` |
| **Publisher** | Salesforce |
| **Tables Ingested** | [`SalesforceServiceCloudV2_CL`](../tables-index.md#salesforceservicecloudv2_cl), [`SalesforceServiceCloud_CL`](../tables-index.md#salesforceservicecloud_cl) |
| **Used in Solutions** | [Salesforce Service Cloud](../solutions/salesforce-service-cloud.md) |
| **Connector Definition Files** | [SalesforceServiceCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud/Data%20Connectors/SalesforceServiceCloud_API_FunctionApp.json) |

The Salesforce Service Cloud data connector provides the capability to ingest information about your Salesforce operational events into Microsoft Sentinel through the REST API. The connector provides ability to review events in your org on an accelerated basis, get [event log files](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/event_log_file_hourly_overview.htm) in hourly increments for recent activity.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
