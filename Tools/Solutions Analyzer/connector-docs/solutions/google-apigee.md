# Google Apigee

## Solution Information

| | |
|------------------------|-------|
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

### [Google ApigeeX (via Codeless Connector Framework)](../connectors/googleapigeexlogsccpdefinition.md)

**Publisher:** Microsoft

The Google ApigeeX data connector provides the capability to ingest Audit logs into Microsoft Sentinel using the Google Apigee API. Refer to [Google Apigee API](https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/?apix=true) documentation for more information.

| | |
|--------------------------|---|
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
