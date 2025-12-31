# ImpervaWAFCloud_CL

## Solutions (1)

This table is used by the following solutions:

- [ImpervaCloudWAF](../solutions/impervacloudwaf.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Imperva Cloud WAF](../connectors/impervawafcloudapi.md)

---

## Content Items Using This Table (21)

### Analytic Rules (10)

**In solution [ImpervaCloudWAF](../solutions/impervacloudwaf.md):**
- [Imperva - Abnormal protocol usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaAbnormalProtocolUsage.yaml)
- [Imperva - Critical severity event not blocked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaAttackNotBlocked.yaml)
- [Imperva - Forbidden HTTP request method in request](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaForbiddenMethod.yaml)
- [Imperva - Malicious Client](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaMaliciousClient.yaml)
- [Imperva - Malicious user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaMaliciousUA.yaml)
- [Imperva - Multiple user agents from same source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaMultipleUAsSource.yaml)
- [Imperva - Possible command injection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaCommandInUri.yaml)
- [Imperva - Request from unexpected IP address to admin panel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaAdminPanelUncommonIp.yaml)
- [Imperva - Request from unexpected countries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaForbiddenCountry.yaml)
- [Imperva - Request to unexpected destination port](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaSuspiciousDstPort.yaml)

### Hunting Queries (10)

**In solution [ImpervaCloudWAF](../solutions/impervacloudwaf.md):**
- [Imperva - Applications with insecure web protocol version](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaInsecureWebProtocolVersion.yaml)
- [Imperva - Non HTTP/HTTPs applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaNonWebApplication.yaml)
- [Imperva - Rare applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaRareApplications.yaml)
- [Imperva - Rare client applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaRareClientApplications.yaml)
- [Imperva - Rare destination ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaRareDstPorts.yaml)
- [Imperva - Top applications with error requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaTopApplicationsErrors.yaml)
- [Imperva - Top destinations with blocked requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaDestinationBlocked.yaml)
- [Imperva - Top sources with blocked requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaSourceBlocked.yaml)
- [Imperva - Top sources with error requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaTopSourcesErrors.yaml)
- [Imperva - request from known bots](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaRequestsFromBots.yaml)

### Workbooks (1)

**In solution [ImpervaCloudWAF](../solutions/impervacloudwaf.md):**
- [Imperva WAF Cloud Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Workbooks/Imperva%20WAF%20Cloud%20Overview.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
