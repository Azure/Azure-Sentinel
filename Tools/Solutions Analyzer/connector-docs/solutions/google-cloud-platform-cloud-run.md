# Google Cloud Platform Cloud Run

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Run](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Run) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [GCP Cloud Run (via Codeless Connector Framework)](../connectors/gcpcloudrunlogs-connectordefinition.md)

**Publisher:** Microsoft

The GCP Cloud Run data connector provides the capability to ingest Cloud Run request logs into Microsoft Sentinel using Pub/Sub. Refer the [Cloud Run Overview](https://cloud.google.com/run/docs/logging) for more details.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GCPCloudRun` |
| **Connector Definition Files** | [GCPCloudRunLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Run/Data%20Connectors/GCPCloudRunLog_CCF/GCPCloudRunLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpcloudrunlogs-connectordefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPCloudRun` | [GCP Cloud Run (via Codeless Connector Framework)](../connectors/gcpcloudrunlogs-connectordefinition.md) |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.1      | 02-09-2025                    | GCP Cloud Run **CCF Conector** moving to GA                                        |
| 3.0.0      | 14-07-2025                    | Initial Solution Release and Added new **CCF Data Connector**.  |

[← Back to Solutions Index](../solutions-index.md)
