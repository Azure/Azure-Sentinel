# OracleWebLogicServer_CL

## Solutions (2)

This table is used by the following solutions:

- [CustomLogsAma](../solutions/customlogsama.md)
- [OracleWebLogicServer](../solutions/oracleweblogicserver.md)

## Connectors (2)

This table is ingested by the following connectors:

- [Custom logs via AMA](../connectors/customlogsviaama.md)
- [[Deprecated] Oracle WebLogic Server](../connectors/oracleweblogicserver.md)

---

## Content Items Using This Table (21)

### Analytic Rules (10)

**In solution [OracleWebLogicServer](../solutions/oracleweblogicserver.md):**
- [Oracle - Command in URI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicCommandInURI.yaml)
- [Oracle - Malicious user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicKnownMaliciousUserAgents.yaml)
- [Oracle - Multiple client errors from single IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicMultipleClientErrorsFromSingleIP.yaml)
- [Oracle - Multiple server errors from single IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicMultipleServerErrorsRequestsFromSingleIP.yaml)
- [Oracle - Multiple user agents for single source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicDifferentUAsFromSingleIP.yaml)
- [Oracle - Oracle WebLogic Exploit CVE-2021-2109](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicExploitCVE-2021-2109.yaml)
- [Oracle - Private IP in URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicPrivateIpInUrl.yaml)
- [Oracle - Put file and get file from same IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicPutAndGetFileFromSameIP.yaml)
- [Oracle - Put suspicious file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicPutSuspiciousFiles.yaml)
- [Oracle - Request to sensitive files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Analytic%20Rules/OracleWebLogicRequestToSensitiveFiles.yaml)

### Hunting Queries (10)

**In solution [OracleWebLogicServer](../solutions/oracleweblogicserver.md):**
- [Oracle - Abnormal request size](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicAbnormalRequestSize.yaml)
- [Oracle - Critical event severity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicCriticalEventSeverity.yaml)
- [Oracle - Error messages](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicErrors.yaml)
- [Oracle - Rare URLs requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicRareURLsRequested.yaml)
- [Oracle - Rare user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicUncommonUserAgents.yaml)
- [Oracle - Rare user agents with client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicRareUAWithClientErrors.yaml)
- [Oracle - Request to forbidden files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogic403RequestsFiles.yaml)
- [Oracle - Top URLs client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicUrlClienterrors.yaml)
- [Oracle - Top URLs server errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicUrlServerErrors.yaml)
- [Oracle - Top files requested by users with error](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Hunting%20Queries/OracleWebLogicFilesErrorRequests.yaml)

### Workbooks (1)

**In solution [OracleWebLogicServer](../solutions/oracleweblogicserver.md):**
- [OracleWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Workbooks/OracleWorkbook.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
