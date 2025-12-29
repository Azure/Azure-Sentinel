# QualysVM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2020-12-14 |
| **Last Updated** | 2025-11-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Qualys Vulnerability Management (via Codeless Connector Framework)](../connectors/qualysvmlogsccpdefinition.md)

**Publisher:** Microsoft

The [Qualys Vulnerability Management (VM)](https://www.qualys.com/apps/vulnerability-management/) data connector provides the capability to ingest vulnerability host detection data into Microsoft Sentinel through the Qualys API. The connector provides visibility into host detection data from vulerability scans.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `QualysHostDetectionV3_CL` |
| **Connector Definition Files** | [QualysVMHostLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Data%20Connectors/QualysVMHostLogs_ccp/QualysVMHostLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/qualysvmlogsccpdefinition.md)

### [[DEPRECATED] Qualys Vulnerability Management](../connectors/qualysvulnerabilitymanagement.md)

**Publisher:** Qualys

The [Qualys Vulnerability Management (VM)](https://www.qualys.com/apps/vulnerability-management/) data connector provides the capability to ingest vulnerability host detection data into Microsoft Sentinel through the Qualys API. The connector provides visibility into host detection data from vulerability scans. This connector provides Microsoft Sentinel the capability to view dashboards, create custom alerts, and improve investigation 



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `QualysHostDetectionV2_CL` |
| | `QualysHostDetection_CL` |
| **Connector Definition Files** | [QualysVM_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Data%20Connectors/QualysVM_API_FunctionApp.json) |

[→ View full connector details](../connectors/qualysvulnerabilitymanagement.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `QualysHostDetectionV2_CL` | [[DEPRECATED] Qualys Vulnerability Management](../connectors/qualysvulnerabilitymanagement.md) |
| `QualysHostDetectionV3_CL` | [Qualys Vulnerability Management (via Codeless Connector Framework)](../connectors/qualysvmlogsccpdefinition.md) |
| `QualysHostDetection_CL` | [[DEPRECATED] Qualys Vulnerability Management](../connectors/qualysvulnerabilitymanagement.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                            	|
|-------------|--------------------------------|----------------------------------------------------------------|
| 3.0.7       | 18-11-2025                     | Adding adjustable API partition limit & rate limit protection. |
| 3.0.6       | 18-09-2025                     | Updated Analytic rules, Parsers, and Workbooks in Sentinel solution content for **CCF connector** compatibility.     |
| 3.0.5       | 29-07-2025                     | Removed Deprecated **Data Connector**.							|  
| 3.0.4 	  | 30-06-2025 					   | QualysVM **CCF Data Connector** moving to GA 					|
| 3.0.3       | 27-05-2025                     | New **CCP Connector** added to the Solution.                   |
| 3.0.2       | 08-04-2025                     | Add HostTags to **Data Connector** and **Parsers**.            |
| 3.0.1       | 07-01-2025                     | Removed Custom Entity mappings from **Analytic Rule**.         |
| 3.0.0       | 16-04-2024                     | Added Deploy to Azure Goverment button for Government portal in **Dataconnector**.   |

[← Back to Solutions Index](../solutions-index.md)
