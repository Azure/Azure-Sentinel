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

This solution provides **1 data connector(s)**:

- [[Deprecated] NGINX HTTP Server](../connectors/nginxhttpserver.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`NGINX_CL`](../tables/nginx-cl.md) | [[Deprecated] NGINX HTTP Server](../connectors/nginxhttpserver.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **22 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [NGINX - Command in URI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXCommandsInRequest.yaml) | High | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Core Dump](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXCoreDump.yaml) | High | Impact | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Known malicious user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXKnownMaliciousUserAgent.yaml) | High | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Multiple client errors from single IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXMultipleClientErrorsFromSingleIP.yaml) | Medium | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Multiple server errors from single IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXMultipleServerErrorsFromSingleIP.yaml) | Medium | Impact, InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Multiple user agents for single source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXDifferentUAsFromSingleIP.yaml) | Medium | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Private IP address in URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXPrivateIPinUrl.yaml) | Medium | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Put file and get file from same IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXPutAndGetFileFromSameIP.yaml) | Medium | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Request to sensitive files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXRequestToSensitiveFiles.yaml) | Medium | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Sql injection patterns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXSqlPattern.yaml) | High | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [NGINX - Abnormal request size](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXAbnormalRequestSize.yaml) | Exfiltration, Collection | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Rare URLs requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXRareURLsRequested.yaml) | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Rare files requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXRareFilesRequested.yaml) | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Requests from bots and crawlers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXRequestsFromBotsCrawlers.yaml) | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Requests to unexisting files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXRequestsToUnexistingFiles.yaml) | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Top URLs client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXTopURLsClientErrors.yaml) | Impact, InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Top URLs server errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXTopURLsServerErrors.yaml) | Impact, InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Top files requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXTopFilesRequested.yaml) | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Top files with error requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXTopFilesWithErrorRequests.yaml) | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |
| [NGINX - Uncommon user agent strings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXUncommonUAsString.yaml) | InitialAccess | [`NGINX_CL`](../tables/nginx-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [NGINX](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Workbooks/NGINX.json) | [`NGINX_CL`](../tables/nginx-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [NGINXHTTPServer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Parsers/NGINXHTTPServer.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       |  13-12-2024                    | Removed Deprecated **Data connector**       |
| 3.0.0       |  08-08-2024                    | Deprecating data connectors                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
