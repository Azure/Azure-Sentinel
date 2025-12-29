# NGINX HTTP Server

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-12-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] NGINX HTTP Server](../connectors/nginxhttpserver.md)

**Publisher:** Nginx

The NGINX HTTP Server data connector provides the capability to ingest [NGINX](https://nginx.org/en/) HTTP Server events into Microsoft Sentinel. Refer to [NGINX Logs documentation](https://nginx.org/en/docs/http/ngx_http_log_module.html) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `NGINX_CL` |
| **Connector Definition Files** | [Connector_NGINX_agent.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Data%20Connectors/Connector_NGINX_agent.json) |

[→ View full connector details](../connectors/nginxhttpserver.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `NGINX_CL` | [[Deprecated] NGINX HTTP Server](../connectors/nginxhttpserver.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       |  13-12-2024                    | Removed Deprecated **Data connector**       |
| 3.0.0       |  08-08-2024                    | Deprecating data connectors                 |

[← Back to Solutions Index](../solutions-index.md)
