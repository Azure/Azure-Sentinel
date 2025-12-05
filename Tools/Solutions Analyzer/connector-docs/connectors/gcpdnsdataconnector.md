# [DEPRECATED] Google Cloud Platform DNS

| | |
|----------|-------|
| **Connector ID** | `GCPDNSDataConnector` |
| **Publisher** | Google |
| **Tables Ingested** | [`GCP_DNS_CL`](../tables-index.md#gcp_dns_cl) |
| **Used in Solutions** | [GoogleCloudPlatformDNS](../solutions/googlecloudplatformdns.md) |
| **Connector Definition Files** | [GCP_DNS_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Data%20Connectors/GCP_DNS_API_FunctionApp.json) |

The Google Cloud Platform DNS data connector provides the capability to ingest [Cloud DNS query logs](https://cloud.google.com/dns/docs/monitoring#using_logging) and [Cloud DNS audit logs](https://cloud.google.com/dns/docs/audit-logging) into Microsoft Sentinel using the GCP Logging API. Refer to [GCP Logging API documentation](https://cloud.google.com/logging/docs/api) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
