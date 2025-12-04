# GoogleCloudPlatformDNS

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] Google Cloud Platform DNS](../connectors/gcpdnsdataconnector.md)

**Publisher:** Google

The Google Cloud Platform DNS data connector provides the capability to ingest [Cloud DNS query logs](https://cloud.google.com/dns/docs/monitoring#using_logging) and [Cloud DNS audit logs](https://cloud.google.com/dns/docs/audit-logging) into Microsoft Sentinel using the GCP Logging API. Refer to [GCP Logging API documentation](https://cloud.google.com/logging/docs/api) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| | |
|--------------------------|---|
| **Tables Ingested** | `GCP_DNS_CL` |
| **Connector Definition Files** | [GCP_DNS_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Data%20Connectors/GCP_DNS_API_FunctionApp.json) |

[→ View full connector details](../connectors/gcpdnsdataconnector.md)

### [Google Cloud Platform DNS (via Codeless Connector Framework)](../connectors/gcpdnslogsccpdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform DNS data connector provides the capability to ingest Cloud DNS Query logs and Cloud DNS Audit logs into Microsoft Sentinel using the Google Cloud DNS API. Refer to [Cloud DNS API](https://cloud.google.com/dns/docs/reference/rest/v1) documentation for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `GCPDNS` |
| **Connector Definition Files** | [GCPDNSLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Data%20Connectors/GCPDNSLog_CCP/GCPDNSLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpdnslogsccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPDNS` | 1 connector(s) |
| `GCP_DNS_CL` | [DEPRECATED] Google Cloud Platform DNS |

[← Back to Solutions Index](../solutions-index.md)
