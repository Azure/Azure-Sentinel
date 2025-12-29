# Google Cloud Platform Cloud Monitoring

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-07-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Monitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Monitoring) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Google Cloud Platform Cloud Monitoring (via Codeless Connector Framework)](../connectors/gcpmonitorccpdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform Cloud Monitoring data connector ingests Monitoring logs from Google Cloud into Microsoft Sentinel using the Google Cloud Monitoring API. Refer to [Cloud Monitoring API](https://cloud.google.com/monitoring/api/v3) documentation for more details.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GCPMonitoring` |
| **Connector Definition Files** | [GCPCloudMonitoringLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Monitoring/Data%20Connectors/GCPMonitoringLogs_CCP/GCPCloudMonitoringLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpmonitorccpdefinition.md)

### [[DEPRECATED] Google Cloud Platform Cloud Monitoring](../connectors/gcpmonitordataconnector.md)

**Publisher:** Google

The Google Cloud Platform Cloud Monitoring data connector provides the capability to ingest [GCP Monitoring metrics](https://cloud.google.com/monitoring/api/metrics_gcp) into Microsoft Sentinel using the GCP Monitoring API. Refer to [GCP Monitoring API documentation](https://cloud.google.com/monitoring/api/v3) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GCP_MONITORING_CL` |
| **Connector Definition Files** | [GCP_Monitor_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Monitoring/Data%20Connectors/GCP_Monitor_API_FunctionApp.json) |

[→ View full connector details](../connectors/gcpmonitordataconnector.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPMonitoring` | [Google Cloud Platform Cloud Monitoring (via Codeless Connector Framework)](../connectors/gcpmonitorccpdefinition.md) |
| `GCP_MONITORING_CL` | [[DEPRECATED] Google Cloud Platform Cloud Monitoring](../connectors/gcpmonitordataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
