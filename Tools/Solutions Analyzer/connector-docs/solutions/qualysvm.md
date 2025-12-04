# QualysVM

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2020-12-14 |
| **Last Updated** | 2025-11-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### Qualys Vulnerability Management (via Codeless Connector Framework)

**Publisher:** Microsoft

The [Qualys Vulnerability Management (VM)](https://www.qualys.com/apps/vulnerability-management/) data connector provides the capability to ingest vulnerability host detection data into Microsoft Sentinel through the Qualys API. The connector provides visibility into host detection data from vulerability scans.

**Tables Ingested:**

- `QualysHostDetectionV3_CL`

**Connector Definition Files:**

- [QualysVMHostLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Data%20Connectors/QualysVMHostLogs_ccp/QualysVMHostLogs_ConnectorDefinition.json)

### [DEPRECATED] Qualys Vulnerability Management

**Publisher:** Qualys

The [Qualys Vulnerability Management (VM)](https://www.qualys.com/apps/vulnerability-management/) data connector provides the capability to ingest vulnerability host detection data into Microsoft Sentinel through the Qualys API. The connector provides visibility into host detection data from vulerability scans. This connector provides Microsoft Sentinel the capability to view dashboards, create custom alerts, and improve investigation 



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

**Tables Ingested:**

- `QualysHostDetectionV2_CL`
- `QualysHostDetection_CL`

**Connector Definition Files:**

- [QualysVM_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Data%20Connectors/QualysVM_API_FunctionApp.json)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `QualysHostDetectionV2_CL` | [DEPRECATED] Qualys Vulnerability Management |
| `QualysHostDetectionV3_CL` | 1 connector(s) |
| `QualysHostDetection_CL` | [DEPRECATED] Qualys Vulnerability Management |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n