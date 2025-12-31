# OracleWebLogicServer

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Oracle WebLogic Server](../connectors/oracleweblogicserver.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) | [[Deprecated] Oracle WebLogic Server](../connectors/oracleweblogicserver.md) | Analytics, Hunting, Workbooks |
| [`TomcatEvent`](../tables/tomcatevent.md) | - | Workbooks |

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
| [Oracle - Command in URI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicCommandInURI.yaml) | High | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Malicious user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicKnownMaliciousUserAgents.yaml) | High | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Multiple client errors from single IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicMultipleClientErrorsFromSingleIP.yaml) | Medium | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Multiple server errors from single IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicMultipleServerErrorsRequestsFromSingleIP.yaml) | Medium | Impact, InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Multiple user agents for single source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicDifferentUAsFromSingleIP.yaml) | Medium | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Oracle WebLogic Exploit CVE-2021-2109](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicExploitCVE-2021-2109.yaml) | High | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Private IP in URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicPrivateIpInUrl.yaml) | Medium | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Put file and get file from same IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicPutAndGetFileFromSameIP.yaml) | Medium | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Put suspicious file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicPutSuspiciousFiles.yaml) | Medium | InitialAccess, Exfiltration | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Request to sensitive files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicRequestToSensitiveFiles.yaml) | High | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Oracle - Abnormal request size](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicAbnormalRequestSize.yaml) | Exfiltration, Collection | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Critical event severity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicCriticalEventSeverity.yaml) | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Error messages](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicErrors.yaml) | DefenseEvasion | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Rare URLs requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicRareURLsRequested.yaml) | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Rare user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicUncommonUserAgents.yaml) | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Rare user agents with client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicRareUAWithClientErrors.yaml) | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Request to forbidden files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogic403RequestsFiles.yaml) | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Top URLs client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicUrlClienterrors.yaml) | Impact, InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Top URLs server errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicUrlServerErrors.yaml) | Impact, InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |
| [Oracle - Top files requested by users with error](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicFilesErrorRequests.yaml) | InitialAccess | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [OracleWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Workbooks/OracleWorkbook.json) | [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md)<br>[`TomcatEvent`](../tables/tomcatevent.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [OracleWebLogicServerEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Parsers/OracleWebLogicServerEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------|
| 3.0.2       | 23-12-2024                     | Removed Deprecated **Data connector**                                        |
| 3.0.1       | 09-08-2024                     | Deprecating data connectors                                                  |
| 3.0.0       | 15-12-2023                     | Updated the **Parser** field TreadId to ThreadId                             |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
