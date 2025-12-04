# GoogleCloudPlatformIDS

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIDS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIDS) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Google Cloud Platform Cloud IDS (via Codeless Connector Framework)

**Publisher:** Microsoft

The Google Cloud Platform IDS data connector provides the capability to ingest Cloud IDS Traffic logs, Threat logs and Audit logs into Microsoft Sentinel using the Google Cloud IDS API. Refer to [Cloud IDS API](https://cloud.google.com/intrusion-detection-system/docs/audit-logging#google.cloud.ids.v1.IDS) documentation for more information.

**Tables Ingested:**

- `GCPIDS`

**Connector Definition Files:**

- [GCPCloudIDSLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIDS/Data%20Connectors/GCPCloudIDSLog_CCP/GCPCloudIDSLog_ConnectorDefinition.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPIDS` | 1 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n