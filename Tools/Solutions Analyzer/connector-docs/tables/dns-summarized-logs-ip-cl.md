# DNS_Summarized_Logs_ip_CL

> **Internal Use Table:** This table is created and used internally by the [DNS Essentials](../solutions/dns-essentials.md) solution. It is written to by playbooks for solution-specific data storage.

| Attribute | Value |
|:----------|:------|
| **Category** | Internal |

## Solutions (1)

This table is used by the following solutions:

- [DNS Essentials](../solutions/dns-essentials.md)

---

## Content Items Using This Table (7)

### Analytic Rules (3)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [Detect DNS queries reporting multiple errors from different clients - Anomaly Based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/MultipleErrorsReportedForSameDNSQueryAnomalyBased.yaml)
- [Detect excessive NXDOMAIN DNS queries - Anomaly based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/ExcessiveNXDOMAINDNSQueriesAnomalyBased.yaml)
- [Potential DGA(Domain Generation Algorithm) detected via Repetitive Failures - Anomaly based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/PotentialDGADetectedviaRepetitiveFailuresAnomalyBased.yaml)

### Hunting Queries (2)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [Connection to Unpopular Website Detected (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/ConnectionToUnpopularWebsiteDetected.yaml)
- [[Anomaly] Anomalous Increase in DNS activity by clients (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/AnomalousIncreaseInDNSActivityByClients.yaml)

### Workbooks (1)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [DNSSolutionWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Workbooks/DNSSolutionWorkbook.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
