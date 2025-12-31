# GCP_DNS_CL

| Attribute | Value |
|:----------|:------|
| **Category** | GCP |

## Solutions (7)

This table is used by the following solutions:

- [DNS Essentials](../solutions/dns-essentials.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [GoogleCloudPlatformDNS](../solutions/googlecloudplatformdns.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Recorded Future](../solutions/recorded-future.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)

## Connectors (1)

This table is ingested by the following connectors:

- [[DEPRECATED] Google Cloud Platform DNS](../connectors/gcpdnsdataconnector.md)

---

## Content Items Using This Table (52)

### Analytic Rules (26)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [Detect DNS queries reporting multiple errors from different clients - Anomaly Based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/MultipleErrorsReportedForSameDNSQueryAnomalyBased.yaml)
- [Detect DNS queries reporting multiple errors from different clients - Static threshold based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/MultipleErrorsReportedForSameDNSQueryStaticThresholdBased.yaml)
- [Detect excessive NXDOMAIN DNS queries - Anomaly based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/ExcessiveNXDOMAINDNSQueriesAnomalyBased.yaml)
- [Detect excessive NXDOMAIN DNS queries - Static threshold based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/ExcessiveNXDOMAINDNSQueriesStaticThresholdBased.yaml)
- [Ngrok Reverse Proxy on Network (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/NgrokReverseProxyOnNetwork.yaml)
- [Potential DGA(Domain Generation Algorithm) detected via Repetitive Failures - Anomaly based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/PotentialDGADetectedviaRepetitiveFailuresAnomalyBased.yaml)
- [Potential DGA(Domain Generation Algorithm) detected via Repetitive Failures - Static threshold based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/PotentialDGADetectedviaRepetitiveFailuresStaticThresholdBased.yaml)
- [Rare client observed with high reverse DNS lookup count - Anomaly based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/RareClientObservedWithHighReverseDNSLookupCountAnomalyBased.yaml)
- [Rare client observed with high reverse DNS lookup count - Static threshold based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/RareClientObservedWithHighReverseDNSLookupCountStaticThresholdBased.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntDomain.yaml)

**In solution [GoogleCloudPlatformDNS](../solutions/googlecloudplatformdns.md):**
- [Google DNS - CVE-2020-1350 (SIGRED) exploitation pattern](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSSIGREDPattern.yaml)
- [Google DNS - CVE-2021-34527 (PrintNightmare) external exploit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSPrintNightmare.yaml)
- [Google DNS - CVE-2021-40444 exploitation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSCVE-2021-40444.yaml)
- [Google DNS - Exchange online autodiscover abuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSExchangeAutodiscoverAbuse.yaml)
- [Google DNS - IP check activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSIpCheck.yaml)
- [Google DNS - Malicous Python packages](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSMaliciousPythonPackages.yaml)
- [Google DNS - Multiple errors for source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSMultipleErrorsFromIp.yaml)
- [Google DNS - Multiple errors to same domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSMultipleErrorsQuery.yaml)
- [Google DNS - Possible data exfiltration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSDataExfiltration.yaml)
- [Google DNS - Request to dynamic DNS service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSIpDynDns.yaml)
- [Google DNS - UNC2452 (Nobelium) APT Group activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSUNC2452AptActivity.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingDomainAllActors.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml)
- [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml)
- [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml)

### Hunting Queries (22)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [CVE-2020-1350 (SIGRED) exploitation pattern (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/CVE-2020-1350%20%28SIGRED%29ExploitationPattern.yaml)
- [Connection to Unpopular Website Detected (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/ConnectionToUnpopularWebsiteDetected.yaml)
- [Increase in DNS Requests by client than the daily average count (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/IncreaseInDNSRequestsByClientThanTheDailyAverageCount.yaml)
- [Possible DNS Tunneling or Data Exfiltration Activity (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/PossibleDNSTunnelingOrDataExfiltrationActivity.yaml)
- [Potential beaconing activity (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/PotentialBeaconingActivity.yaml)
- [Top 25 DNS queries with most failures in last 24 hours (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/DNSQueryWithFailuresInLast24Hours.yaml)
- [Top 25 Domains with large number of Subdomains (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/DomainsWithLargeNumberOfSubDomains.yaml)
- [Top 25 Sources(Clients) with high number of errors in last 24hours (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/Sources%28Clients%29WithHighNumberOfErrors.yaml)
- [Unexpected top level domains (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/UnexpectedTopLevelDomains.yaml)
- [[Anomaly] Anomalous Increase in DNS activity by clients (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/AnomalousIncreaseInDNSActivityByClients.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntDomain.yaml)

**In solution [GoogleCloudPlatformDNS](../solutions/googlecloudplatformdns.md):**
- [Google DNS - Domains with rare errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSRareErrors.yaml)
- [Google DNS - Errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSErrors.yaml)
- [Google DNS - Rare domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSRareDomains.yaml)
- [Google DNS - Requests to IP lookup resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSIpLookup.yaml)
- [Google DNS - Requests to TOR resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSRequestToTOR.yaml)
- [Google DNS - Requests to online shares](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSOnlineShares.yaml)
- [Google DNS - Server latency](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSServerLatency.yaml)
- [Google DNS - Sources with high number of errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSSourceHighErrors.yaml)
- [Google DNS - Unexpected top level domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSUnexpectedTLD.yaml)
- [Google DNS - Unusual top level domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSUnusualTLD.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureDomainThreatActorHunt.yaml)

### Workbooks (3)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [DNSSolutionWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Workbooks/DNSSolutionWorkbook.json)

**In solution [GoogleCloudPlatformDNS](../solutions/googlecloudplatformdns.md):**
- [GCPDNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Workbooks/GCPDNS.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
