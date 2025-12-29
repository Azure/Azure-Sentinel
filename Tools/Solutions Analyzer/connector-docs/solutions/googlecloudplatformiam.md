# GoogleCloudPlatformIAM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Google Cloud Platform IAM (via Codeless Connector Framework)](../connectors/gcpiamccpdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform IAM data connector provides the capability to ingest the Audit logs relating to Identity and Access Management (IAM) activities within Google Cloud into Microsoft Sentinel using the Google IAM API. Refer to [GCP IAM API](https://cloud.google.com/iam/docs/reference/rest) documentation for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GCPIAM` |
| **Connector Definition Files** | [GCPIAMLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Data%20Connectors/GCPIAMLog_CCP/GCPIAMLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpiamccpdefinition.md)

### [[DEPRECATED] Google Cloud Platform IAM](../connectors/gcpiamdataconnector.md)

**Publisher:** Google

The Google Cloud Platform Identity and Access Management (IAM) data connector provides the capability to ingest [GCP IAM logs](https://cloud.google.com/iam/docs/audit-logging) into Microsoft Sentinel using the GCP Logging API. Refer to [GCP Logging API documentation](https://cloud.google.com/logging/docs/api) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GCP_IAM_CL` |
| **Connector Definition Files** | [GCP_IAM_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Data%20Connectors/GCP_IAM_API_FunctionApp.json) |

[→ View full connector details](../connectors/gcpiamdataconnector.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPIAM` | [Google Cloud Platform IAM (via Codeless Connector Framework)](../connectors/gcpiamccpdefinition.md) |
| `GCP_IAM_CL` | [[DEPRECATED] Google Cloud Platform IAM](../connectors/gcpiamdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
