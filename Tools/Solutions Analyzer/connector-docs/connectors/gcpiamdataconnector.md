# [DEPRECATED] Google Cloud Platform IAM

| | |
|----------|-------|
| **Connector ID** | `GCPIAMDataConnector` |
| **Publisher** | Google |
| **Tables Ingested** | [`GCP_IAM_CL`](../tables-index.md#gcp_iam_cl) |
| **Used in Solutions** | [GoogleCloudPlatformIAM](../solutions/googlecloudplatformiam.md) |
| **Connector Definition Files** | [GCP_IAM_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Data%20Connectors/GCP_IAM_API_FunctionApp.json) |

The Google Cloud Platform Identity and Access Management (IAM) data connector provides the capability to ingest [GCP IAM logs](https://cloud.google.com/iam/docs/audit-logging) into Microsoft Sentinel using the GCP Logging API. Refer to [GCP Logging API documentation](https://cloud.google.com/logging/docs/api) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
