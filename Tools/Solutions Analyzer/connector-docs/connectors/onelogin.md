# [DEPRECATED] OneLogin IAM Platform

| | |
|----------|-------|
| **Connector ID** | `OneLogin` |
| **Publisher** | OneLogin |
| **Tables Ingested** | [`OneLoginEventsV2_CL`](../tables-index.md#onelogineventsv2_cl), [`OneLoginUsersV2_CL`](../tables-index.md#oneloginusersv2_cl), [`OneLogin_CL`](../tables-index.md#onelogin_cl) |
| **Used in Solutions** | [OneLoginIAM](../solutions/oneloginiam.md) |
| **Connector Definition Files** | [OneLogin_Webhooks_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneLoginIAM/Data%20Connectors/OneLogin_Webhooks_FunctionApp.json) |

The [OneLogin](https://www.onelogin.com/) data connector provides the capability to ingest common OneLogin IAM Platform events into Microsoft Sentinel through Webhooks. The OneLogin Event Webhook API which is also known as the Event Broadcaster will send batches of events in near real-time to an endpoint that you specify. When a change occurs in the OneLogin, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://developers.onelogin.com/api-docs/1/events/webhooks) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
