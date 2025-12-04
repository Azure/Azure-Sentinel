# GoogleCloudPlatformSQL

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformSQL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformSQL) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [GCP Cloud SQL (via Codeless Connector Framework)](../connectors/gcpcloudsqlccfdefinition.md)

**Publisher:** Microsoft

The GCP Cloud SQL data connector provides the capability to ingest Audit logs into Microsoft Sentinel using the GCP Cloud SQL API. Refer to [GCP cloud SQL Audit Logs](https://cloud.google.com/sql/docs/mysql/audit-logging) documentation for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `GCPCloudSQL` |
| **Connector Definition Files** | [GCPCloudSQLLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformSQL/Data%20Connectors/GCPCloudSQLLog_CCF/GCPCloudSQLLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpcloudsqlccfdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPCloudSQL` | [GCP Cloud SQL (via Codeless Connector Framework)](../connectors/gcpcloudsqlccfdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
