# Cloudflare

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

The Cloudflare data connector provides the capability to ingest [Cloudflare logs](https://developers.cloudflare.com/logs/) into Microsoft Sentinel using the Cloudflare Logpush and Azure Blob Storage. Refer to [Cloudflare  documentation](https://developers.cloudflare.com/logs/logpush) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Cloudflare_CL` |
| **Connector Definition Files** | [Cloudflare_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Data%20Connectors/Cloudflare_API_FunctionApp.json) |

[→ View full connector details](../connectors/cloudflaredataconnector.md)

### [Cloudflare (Using Blob Container) (via Codeless Connector Framework)](../connectors/cloudflaredefinition.md)

**Publisher:** Microsoft

 The Cloudflare data connector provides the capability to ingest Cloudflare logs into Microsoft Sentinel using the Cloudflare Logpush and Azure Blob Storage. Refer to [Cloudflare documentation](https://developers.cloudflare.com/logs/about/)for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CloudflareV2_CL` |
| **Connector Definition Files** | [CloudflareLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Data%20Connectors/CloudflareLog_CCF/CloudflareLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/cloudflaredefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CloudflareV2_CL` | [Cloudflare (Using Blob Container) (via Codeless Connector Framework)](../connectors/cloudflaredefinition.md) |
| `Cloudflare_CL` | [[DEPRECATED] Cloudflare](../connectors/cloudflaredataconnector.md) |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.2      | 05-09-2024                    | Updated the python runtime version to 3.11                                                |
| 3.0.1      | 01-08-2023                    | Updated logic in **Data Connector** to handle broken events.                              |
| 3.0.0      | 24-07-2023                    | Updated logic in **Hunting Query** (Cloudflare - Client errors,Cloudflare - Server errors)|

[← Back to Solutions Index](../solutions-index.md)
