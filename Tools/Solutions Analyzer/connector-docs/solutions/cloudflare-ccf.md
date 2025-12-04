# Cloudflare CCF

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cloudflare |
| **Support Tier** | Partner |
| **Support Link** | [https://support.cloudflare.com](https://support.cloudflare.com) |
| **Categories** | domains |
| **First Published** | 2025-09-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare%20CCF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare%20CCF) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cloudflare (Using Blob Container) (via Codeless Connector Framework)](../connectors/cloudflaredefinition.md)

**Publisher:** Microsoft

 The Cloudflare data connector provides the capability to ingest Cloudflare logs into Microsoft Sentinel using the Cloudflare Logpush and Azure Blob Storage. Refer to [Cloudflare documentation](https://developers.cloudflare.com/logs/about/)for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `CloudflareV2_CL` |
| **Connector Definition Files** | [CloudflareLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare%20CCF/Data%20Connectors/CloudflareLog_CCF/CloudflareLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/cloudflaredefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CloudflareV2_CL` | [Cloudflare (Using Blob Container) (via Codeless Connector Framework)](../connectors/cloudflaredefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
