# [DEPRECATED] Google Cloud Platform Cloud Monitoring

| | |
|----------|-------|
| **Connector ID** | `GCPMonitorDataConnector` |
| **Publisher** | Google |
| **Tables Ingested** | [`GCP_MONITORING_CL`](../tables-index.md#gcp_monitoring_cl) |
| **Used in Solutions** | [Google Cloud Platform Cloud Monitoring](../solutions/google-cloud-platform-cloud-monitoring.md) |
| **Connector Definition Files** | [GCP_Monitor_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Monitoring/Data%20Connectors/GCP_Monitor_API_FunctionApp.json) |

The Google Cloud Platform Cloud Monitoring data connector provides the capability to ingest [GCP Monitoring metrics](https://cloud.google.com/monitoring/api/metrics_gcp) into Microsoft Sentinel using the GCP Monitoring API. Refer to [GCP Monitoring API documentation](https://cloud.google.com/monitoring/api/v3) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
