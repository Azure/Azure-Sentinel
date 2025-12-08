# [DEPRECATED] Oracle Cloud Infrastructure

| | |
|----------|-------|
| **Connector ID** | `OracleCloudInfrastructureLogsConnector` |
| **Publisher** | Oracle |
| **Tables Ingested** | [`OCI_Logs_CL`](../tables-index.md#oci_logs_cl) |
| **Used in Solutions** | [Oracle Cloud Infrastructure](../solutions/oracle-cloud-infrastructure.md) |
| **Connector Definition Files** | [OCI_logs_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Data%20Connectors/OCI_logs_API_FunctionApp.json) |

The Oracle Cloud Infrastructure (OCI) data connector provides the capability to ingest OCI Logs from [OCI Stream](https://docs.oracle.com/iaas/Content/Streaming/Concepts/streamingoverview.htm) into Microsoft Sentinel using the [OCI Streaming REST API](https://docs.oracle.com/iaas/api/#/streaming/streaming/20180418).



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
