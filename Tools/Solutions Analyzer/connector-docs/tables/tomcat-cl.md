# Tomcat_CL

## Solutions (2)

This table is used by the following solutions:

- [CustomLogsAma](../solutions/customlogsama.md)
- [Tomcat](../solutions/tomcat.md)

## Connectors (2)

This table is ingested by the following connectors:

- [[Deprecated] Apache Tomcat](../connectors/apachetomcat.md)
- [Custom logs via AMA](../connectors/customlogsviaama.md)

---

## Content Items Using This Table (22)

### Analytic Rules (10)

**In solution [Tomcat](../solutions/tomcat.md):**
- [Tomcat - Commands in URI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatCommandsinRequest.yaml)
- [Tomcat - Known malicious user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatKnownMaliciousUserAgent.yaml)
- [Tomcat - Multiple client errors from single IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatMultipleClientErrorsFromSingleIP.yaml)
- [Tomcat - Multiple empty requests from same IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatMultipleEmptyRequestsFromSameIP.yaml)
- [Tomcat - Multiple server errors from single IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatMultipleServerErrorsFromSingleIP.yaml)
- [Tomcat - Put file and get file from same IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatPutAndGetFileFromSameIP.yaml)
- [Tomcat - Request from localhost IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatRequestFromLocalhostIP.yaml)
- [Tomcat - Request to sensitive files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatRequestSensitiveFiles.yaml)
- [Tomcat - Server errors after multiple requests from same IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatServerErrorsAfterMultipleRequestsFromSameIP.yaml)
- [Tomcat - Sql injection patterns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Analytic%20Rules/TomcatSQLiPattern.yaml)

### Hunting Queries (11)

**In solution [Tomcat](../solutions/tomcat.md):**
- [Tomcat - Abnormal request size](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatAbnormalRequestSize.yaml)
- [Tomcat - Catalina errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatERRORs.yaml)
- [Tomcat - Rare URLs requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatRareURLsRequested.yaml)
- [Tomcat - Rare files requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatRareFilesRequested.yaml)
- [Tomcat - Rare user agents with client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatUncommonUAsWithClientErrors.yaml)
- [Tomcat - Rare user agents with server errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatUncommonUAsWithServerErrors.yaml)
- [Tomcat - Request to forbidden file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/Tomcat403RequestsFiles.yaml)
- [Tomcat - Top URLs client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatTopURLsClientErrors.yaml)
- [Tomcat - Top URLs server errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatTopURLsServerErrors.yaml)
- [Tomcat - Top files with error requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatTopFilesWithErrorRequests.yaml)
- [Tomcat - Uncommon user agent strings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Hunting%20Queries/TomcatUncommonUAs.yaml)

### Workbooks (1)

**In solution [Tomcat](../solutions/tomcat.md):**
- [Tomcat](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Workbooks/Tomcat.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
