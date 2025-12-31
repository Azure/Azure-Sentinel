# ApacheHTTPServer

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Apache HTTP Server](../connectors/apachehttpserver.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) | [[Deprecated] Apache HTTP Server](../connectors/apachehttpserver.md) | Analytics, Hunting, Workbooks |

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
| [Apache - Apache 2.4.49 flaw CVE-2021-41773](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Analytic%20Rules/ApacheCVE-2021-41773.yaml) | High | InitialAccess, LateralMovement | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Command in URI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Analytic%20Rules/ApacheCommandInURI.yaml) | High | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Known malicious user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Analytic%20Rules/ApacheKnownMaliciousUserAgents.yaml) | High | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Multiple client errors from single IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Analytic%20Rules/ApacheMultipleClientErrorsFromSingleIP.yaml) | Medium | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Multiple server errors from single IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Analytic%20Rules/ApacheMultipleServerErrorsRequestsFromSingleIP.yaml) | Medium | Impact, InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Private IP in URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Analytic%20Rules/ApachePrivateIpInUrl.yaml) | Medium | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Put suspicious file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Analytic%20Rules/ApachePutSuspiciousFiles.yaml) | Medium | InitialAccess, Exfiltration | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Request from private IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Analytic%20Rules/ApacheRequestFromPrivateIP.yaml) | Medium | Impact, InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Request to sensitive files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Analytic%20Rules/ApacheRequestToSensitiveFiles.yaml) | Medium | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Requests to rare files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Analytic%20Rules/ApacheRequestToRareFile.yaml) | Medium | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Apache - Rare URLs requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Hunting%20Queries/ApacheRareURLsRequested.yaml) | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Rare files requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Hunting%20Queries/ApacheRareFilesRequested.yaml) | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Rare user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Hunting%20Queries/ApacheRareUserAgents.yaml) | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Rare user agents with client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Hunting%20Queries/ApacheRareUAWithClientErrors.yaml) | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Requests to unexisting files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Hunting%20Queries/ApacheRequestsToUnexistingFiles.yaml) | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Top Top files requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Hunting%20Queries/ApacheFilesRequested.yaml) | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Top URLs with client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Hunting%20Queries/ApacheUrlClienterrors.yaml) | Impact, InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Top URLs with server errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Hunting%20Queries/ApacheUrlServerErrors.yaml) | Impact, InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Top files requested with errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Hunting%20Queries/ApacheFilesErrorRequests.yaml) | InitialAccess | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |
| [Apache - Unexpected Post Requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Hunting%20Queries/ApacheUnexpectedPostRequests.yaml) | Persistence, CommandAndControl | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ApacheHTTPServer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Workbooks/ApacheHTTPServer.json) | [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ApacheHTTPServer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Parsers/ApacheHTTPServer.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 05-12-2024                     | Removed Deprecated **Data connectors**                             |
| 3.0.0       | 13-08-2024                     | Deprecating data connectors                                        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
