# Oracle Cloud Infrastructure

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Oracle Cloud Infrastructure (via Codeless Connector Framework)](../connectors/oci-connector-ccp-definition.md)

**Publisher:** Microsoft

### [[DEPRECATED] Oracle Cloud Infrastructure](../connectors/oraclecloudinfrastructurelogsconnector.md)

**Publisher:** Oracle

The Oracle Cloud Infrastructure (OCI) data connector provides the capability to ingest OCI Logs from [OCI Stream](https://docs.oracle.com/iaas/Content/Streaming/Concepts/streamingoverview.htm) into Microsoft Sentinel using the [OCI Streaming REST API](https://docs.oracle.com/iaas/api/#/streaming/streaming/20180418).



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| | |
|--------------------------|---|
| **Tables Ingested** | `OCI_Logs_CL` |
| **Connector Definition Files** | [OCI_logs_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Data%20Connectors/OCI_logs_API_FunctionApp.json) |

[→ View full connector details](../connectors/oraclecloudinfrastructurelogsconnector.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OCI_LogsV2_CL` | [Oracle Cloud Infrastructure (via Codeless Connector Framework)](../connectors/oci-connector-ccp-definition.md) |
| `OCI_Logs_CL` | [[DEPRECATED] Oracle Cloud Infrastructure](../connectors/oraclecloudinfrastructurelogsconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
