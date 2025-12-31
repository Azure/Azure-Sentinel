# NGINX_CL

## Solutions (2)

This table is used by the following solutions:

- [CustomLogsAma](../solutions/customlogsama.md)
- [NGINX HTTP Server](../solutions/nginx-http-server.md)

## Connectors (2)

This table is ingested by the following connectors:

- [Custom logs via AMA](../connectors/customlogsviaama.md)
- [[Deprecated] NGINX HTTP Server](../connectors/nginxhttpserver.md)

---

## Content Items Using This Table (21)

### Analytic Rules (10)

**In solution [NGINX HTTP Server](../solutions/nginx-http-server.md):**
- [NGINX - Command in URI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXCommandsInRequest.yaml)
- [NGINX - Core Dump](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXCoreDump.yaml)
- [NGINX - Known malicious user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXKnownMaliciousUserAgent.yaml)
- [NGINX - Multiple client errors from single IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXMultipleClientErrorsFromSingleIP.yaml)
- [NGINX - Multiple server errors from single IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXMultipleServerErrorsFromSingleIP.yaml)
- [NGINX - Multiple user agents for single source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXDifferentUAsFromSingleIP.yaml)
- [NGINX - Private IP address in URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXPrivateIPinUrl.yaml)
- [NGINX - Put file and get file from same IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXPutAndGetFileFromSameIP.yaml)
- [NGINX - Request to sensitive files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXRequestToSensitiveFiles.yaml)
- [NGINX - Sql injection patterns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Analytic%20Rules/NGINXSqlPattern.yaml)

### Hunting Queries (10)

**In solution [NGINX HTTP Server](../solutions/nginx-http-server.md):**
- [NGINX - Abnormal request size](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXAbnormalRequestSize.yaml)
- [NGINX - Rare URLs requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXRareURLsRequested.yaml)
- [NGINX - Rare files requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXRareFilesRequested.yaml)
- [NGINX - Requests from bots and crawlers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXRequestsFromBotsCrawlers.yaml)
- [NGINX - Requests to unexisting files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXRequestsToUnexistingFiles.yaml)
- [NGINX - Top URLs client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXTopURLsClientErrors.yaml)
- [NGINX - Top URLs server errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXTopURLsServerErrors.yaml)
- [NGINX - Top files requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXTopFilesRequested.yaml)
- [NGINX - Top files with error requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXTopFilesWithErrorRequests.yaml)
- [NGINX - Uncommon user agent strings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Hunting%20Queries/NGINXUncommonUAsString.yaml)

### Workbooks (1)

**In solution [NGINX HTTP Server](../solutions/nginx-http-server.md):**
- [NGINX](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NGINX%20HTTP%20Server/Workbooks/NGINX.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
