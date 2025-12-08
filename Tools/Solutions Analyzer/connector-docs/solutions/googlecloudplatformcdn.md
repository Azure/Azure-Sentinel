# GoogleCloudPlatformCDN

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-03-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformCDN](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformCDN) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Google Cloud Platform CDN (via Codeless Connector Framework)](../connectors/gcpcdnlogsccpdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform CDN data connector provides the capability to ingest Cloud CDN Audit logs and Cloud CDN Traffic logs into Microsoft Sentinel using the Compute Engine API. Refer the [Product overview](https://cloud.google.com/cdn/docs/overview) document for more details.

| | |
|--------------------------|---|
| **Tables Ingested** | `GCPCDN` |
| **Connector Definition Files** | [GCPCDNLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformCDN/Data%20Connectors/GCPCDNLogs_ccp/GCPCDNLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpcdnlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPCDN` | [Google Cloud Platform CDN (via Codeless Connector Framework)](../connectors/gcpcdnlogsccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
