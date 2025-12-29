# Google Apigee

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Apigee](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Apigee) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] Google ApigeeX](../connectors/apigeexdataconnector.md)

**Publisher:** Google

The [Google ApigeeX](https://cloud.google.com/apigee/docs) data connector provides the capability to ingest ApigeeX audit logs into Microsoft Sentinel using the GCP Logging API. Refer to [GCP Logging API documentation](https://cloud.google.com/logging/docs/reference/v2/rest) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ApigeeX_CL` |
| **Connector Definition Files** | [ApigeeX_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Apigee/Data%20Connectors/ApigeeX_FunctionApp.json) |

[→ View full connector details](../connectors/apigeexdataconnector.md)

### [Google ApigeeX (via Codeless Connector Framework)](../connectors/googleapigeexlogsccpdefinition.md)

**Publisher:** Microsoft

The Google ApigeeX data connector provides the capability to ingest Audit logs into Microsoft Sentinel using the Google Apigee API. Refer to [Google Apigee API](https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/?apix=true) documentation for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GCPApigee` |
| **Connector Definition Files** | [GoogleApigeeXLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Apigee/Data%20Connectors/GoogleApigeeXLog_CCP/GoogleApigeeXLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/googleapigeexlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ApigeeX_CL` | [[DEPRECATED] Google ApigeeX](../connectors/apigeexdataconnector.md) |
| `GCPApigee` | [Google ApigeeX (via Codeless Connector Framework)](../connectors/googleapigeexlogsccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
