# Oracle Cloud Infrastructure

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

The Oracle Cloud Infrastructure (OCI) data connector provides the capability to ingest OCI Logs from [OCI Stream](https://docs.oracle.com/iaas/Content/Streaming/Concepts/streamingoverview.htm) into Microsoft Sentinel using the [OCI Streaming REST API](https://docs.oracle.com/iaas/api/#/streaming/streaming/20180418).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `OCI_LogsV2_CL` |
| **Connector Definition Files** | [OCI_DataConnector_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Data%20Connectors/Oracle_Cloud_Infrastructure_CCP/OCI_DataConnector_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/oci-connector-ccp-definition.md)

### [[DEPRECATED] Oracle Cloud Infrastructure](../connectors/oraclecloudinfrastructurelogsconnector.md)

**Publisher:** Oracle

The Oracle Cloud Infrastructure (OCI) data connector provides the capability to ingest OCI Logs from [OCI Stream](https://docs.oracle.com/iaas/Content/Streaming/Concepts/streamingoverview.htm) into Microsoft Sentinel using the [OCI Streaming REST API](https://docs.oracle.com/iaas/api/#/streaming/streaming/20180418).



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `OCI_Logs_CL` |
| **Connector Definition Files** | [OCI_logs_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Data%20Connectors/OCI_logs_API_FunctionApp.json) |

[→ View full connector details](../connectors/oraclecloudinfrastructurelogsconnector.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OCI_LogsV2_CL` | [Oracle Cloud Infrastructure (via Codeless Connector Framework)](../connectors/oci-connector-ccp-definition.md) |
| `OCI_Logs_CL` | [[DEPRECATED] Oracle Cloud Infrastructure](../connectors/oraclecloudinfrastructurelogsconnector.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                          |
|-------------|--------------------------------|-----------------------------------------------------------------------------|
| 3.0.6       | 09-12-2025                     | Support Multistream + multi partition.       |
| 3.0.5       | 13-11-2025                     | Updated partition id text box's description with zero-based indexing.       |
| 3.0.4       | 22-09-2025                     | Updated the OCI **CCF Data Connector** instructions to include information about the partition ID limitation.		 							 |
| 3.0.3       | 25-08-2025                     | Moving OCI **CCF Data Connector** to GA		 							 |
| 3.0.2       | 14-07-2025                     | Introduced new **CCF Connector** to the Solution - "OCI-Connector-CCP-Definition".|
| 3.0.1       | 05-10-2023                     | Manual deployment instructions updated for **Data Connector**.               |
| 3.0.0       | 21-08-2023                     | Modified the **Parser** by adding Columnifexists condition to avoid errors. |

[← Back to Solutions Index](../solutions-index.md)
