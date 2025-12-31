# Tomcat

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Apache Tomcat](../connectors/apachetomcat.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Tomcat_CL`](../tables/tomcat-cl.md) | [[Deprecated] Apache Tomcat](../connectors/apachetomcat.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **23 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 11 |
| Analytic Rules | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Tomcat - Commands in URI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatCommandsinRequest.yaml) | High | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Known malicious user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatKnownMaliciousUserAgent.yaml) | High | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Multiple client errors from single IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatMultipleClientErrorsFromSingleIP.yaml) | Medium | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Multiple empty requests from same IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatMultipleEmptyRequestsFromSameIP.yaml) | Medium | InitialAccess, Impact | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Multiple server errors from single IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatMultipleServerErrorsFromSingleIP.yaml) | Medium | Impact, InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Put file and get file from same IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatPutAndGetFileFromSameIP.yaml) | Medium | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Request from localhost IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatRequestFromLocalhostIP.yaml) | Medium | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Request to sensitive files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatRequestSensitiveFiles.yaml) | High | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Server errors after multiple requests from same IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatServerErrorsAfterMultipleRequestsFromSameIP.yaml) | Medium | Impact, InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Sql injection patterns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatSQLiPattern.yaml) | High | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Tomcat - Abnormal request size](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatAbnormalRequestSize.yaml) | Exfiltration, Collection | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Catalina errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatERRORs.yaml) | DefenseEvasion | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Rare URLs requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatRareURLsRequested.yaml) | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Rare files requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatRareFilesRequested.yaml) | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Rare user agents with client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatUncommonUAsWithClientErrors.yaml) | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Rare user agents with server errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatUncommonUAsWithServerErrors.yaml) | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Request to forbidden file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/Tomcat403RequestsFiles.yaml) | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Top URLs client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatTopURLsClientErrors.yaml) | Impact, InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Top URLs server errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatTopURLsServerErrors.yaml) | Impact, InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Top files with error requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatTopFilesWithErrorRequests.yaml) | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |
| [Tomcat - Uncommon user agent strings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatUncommonUAs.yaml) | InitialAccess | [`Tomcat_CL`](../tables/tomcat-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Tomcat](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Workbooks/Tomcat.json) | [`Tomcat_CL`](../tables/tomcat-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [TomcatEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Parsers/TomcatEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                  |
|-------------|--------------------------------|-------------------------------------------------------------------------------------|
| 3.0.1       | 09-12-2024                     | Removed Deprecated **Data connector**                                               |
| 3.0.0       | 13-08-2024                     | Deprecating data connectors |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
