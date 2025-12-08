# Google Cloud Platform Cloud Run

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `GCPCloudRun` |
| **Connector Definition Files** | [GCPCloudRunLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Run/Data%20Connectors/GCPCloudRunLog_CCF/GCPCloudRunLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpcloudrunlogs-connectordefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPCloudRun` | [GCP Cloud Run (via Codeless Connector Framework)](../connectors/gcpcloudrunlogs-connectordefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
