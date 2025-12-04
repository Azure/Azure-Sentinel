# Cloudflare

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cloudflare |
| **Support Tier** | Partner |
| **Support Link** | [https://support.cloudflare.com](https://support.cloudflare.com) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] Cloudflare](../connectors/cloudflaredataconnector.md)

**Publisher:** Cloudflare

### [Cloudflare (Using Blob Container) (via Codeless Connector Framework)](../connectors/cloudflaredefinition.md)

**Publisher:** Microsoft

 The Cloudflare data connector provides the capability to ingest Cloudflare logs into Microsoft Sentinel using the Cloudflare Logpush and Azure Blob Storage. Refer to [Cloudflare documentation](https://developers.cloudflare.com/logs/about/)for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `CloudflareV2_CL` |
| **Connector Definition Files** | [CloudflareLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Data%20Connectors/CloudflareLog_CCF/CloudflareLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/cloudflaredefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CloudflareV2_CL` | [Cloudflare (Using Blob Container) (via Codeless Connector Framework)](../connectors/cloudflaredefinition.md) |
| `Cloudflare_CL` | [[DEPRECATED] Cloudflare](../connectors/cloudflaredataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
