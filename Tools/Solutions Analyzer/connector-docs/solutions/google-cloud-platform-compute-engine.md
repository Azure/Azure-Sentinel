# Google Cloud Platform Compute Engine

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Compute%20Engine](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Compute%20Engine) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Google Cloud Platform Compute Engine (via Codeless Connector Framework)](../connectors/gcpcomputeenginelogsccpdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform Compute Engine data connector provides the capability to ingest Compute Engine Audit logs into Microsoft Sentinel using the Google Cloud Compute Engine API. Refer to [Cloud Compute Engine API](https://cloud.google.com/compute/docs/reference/rest/v1) documentation for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `GCPComputeEngine` |
| **Connector Definition Files** | [GCPComputeEngineLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Compute%20Engine/Data%20Connectors/GCPComputeEngineLog_CCP/GCPComputeEngineLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpcomputeenginelogsccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPComputeEngine` | [Google Cloud Platform Compute Engine (via Codeless Connector Framework)](../connectors/gcpcomputeenginelogsccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
