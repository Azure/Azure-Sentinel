# Cisco_Umbrella_dns_CL

## Solutions (7)

This table is used by the following solutions:

- [CiscoUmbrella](../solutions/ciscoumbrella.md)
- [DNS Essentials](../solutions/dns-essentials.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Recorded Future](../solutions/recorded-future.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)

## Connectors (2)

This table is ingested by the following connectors:

- [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md)
- [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md)

---

## Content Items Using This Table (51)

### Analytic Rules (25)

**In solution [CiscoUmbrella](../solutions/ciscoumbrella.md):**
- [Cisco Cloud Security - Connection to Unpopular Website Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Analytic%20Rules/CiscoUmbrellaConnectionToUnpopularWebsiteDetected.yaml)
- [Cisco Cloud Security - Connection to non-corporate private network](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Analytic%20Rules/CiscoUmbrellaConnectionNon-CorporatePrivateNetwork.yaml)
- [Cisco Cloud Security - Crypto Miner User-Agent Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Analytic%20Rules/CiscoUmbrellaCryptoMinerUserAgentDetected.yaml)
- [Cisco Cloud Security - Empty User Agent Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Analytic%20Rules/CiscoUmbrellaEmptyUserAgentDetected.yaml)
- [Cisco Cloud Security - Hack Tool User-Agent Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Analytic%20Rules/CiscoUmbrellaHackToolUserAgentDetected.yaml)
- [Cisco Cloud Security - Rare User Agent Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Analytic%20Rules/CiscoUmbrellaRareUserAgentDetected.yaml)
- [Cisco Cloud Security - Request Allowed to harmful/malicious URI category](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Analytic%20Rules/CiscoUmbrellaRequestAllowedHarmfulMaliciousURICategory.yaml)
- [Cisco Cloud Security - Request to blocklisted file type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Analytic%20Rules/CiscoUmbrellaRequestBlocklistedFileType.yaml)
- [Cisco Cloud Security - URI contains IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Analytic%20Rules/CiscoUmbrellaURIContainsIPAddress.yaml)
- [Cisco Cloud Security - Windows PowerShell User-Agent Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Analytic%20Rules/CiscoUmbrellaPowershellUserAgentDetected.yaml)

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

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingDomainAllActors.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml)
- [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml)
- [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml)

### Hunting Queries (22)

**In solution [CiscoUmbrella](../solutions/ciscoumbrella.md):**
- [Cisco Cloud Security - 'Blocked' User-Agents.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Hunting%20Queries/CiscoUmbrellaBlockedUserAgents.yaml)
- [Cisco Cloud Security - Anomalous FQDNs for domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Hunting%20Queries/CiscoUmbrellaAnomalousFQDNsforDomain.yaml)
- [Cisco Cloud Security - DNS Errors.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Hunting%20Queries/CiscoUmbrellaDNSErrors.yaml)
- [Cisco Cloud Security - DNS requests to unreliable categories.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Hunting%20Queries/CiscoUmbrellaDNSRequestsUunreliableCategory.yaml)
- [Cisco Cloud Security - High values of Uploaded Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Hunting%20Queries/CiscoUmbrellaHighValuesOfUploadedData.yaml)
- [Cisco Cloud Security - Higher values of count of the Same BytesIn size](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Hunting%20Queries/CiscoUmbrellaHighCountsOfTheSameBytesInSize.yaml)
- [Cisco Cloud Security - Possible connection to C2.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Hunting%20Queries/CiscoUmbrellaPossibleConnectionC2.yaml)
- [Cisco Cloud Security - Possible data exfiltration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Hunting%20Queries/CiscoUmbrellaPossibleDataExfiltration.yaml)
- [Cisco Cloud Security - Proxy 'Allowed' to unreliable categories.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Hunting%20Queries/CiscoUmbrellaProxyAllowedUnreliableCategory.yaml)
- [Cisco Cloud Security - Requests to uncategorized resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Hunting%20Queries/CiscoUmbrellaRequestsUncategorizedURI.yaml)

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

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureDomainThreatActorHunt.yaml)

### Workbooks (3)

**In solution [CiscoUmbrella](../solutions/ciscoumbrella.md):**
- [CiscoUmbrella](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Workbooks/CiscoUmbrella.json)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [DNSSolutionWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Workbooks/DNSSolutionWorkbook.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
