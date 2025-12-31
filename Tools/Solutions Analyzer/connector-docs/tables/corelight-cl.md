# Corelight_CL

## Solutions (11)

This table is used by the following solutions:

- [Corelight](../solutions/corelight.md)
- [DNS Essentials](../solutions/dns-essentials.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Network Session Essentials](../solutions/network-session-essentials.md)
- [Recorded Future](../solutions/recorded-future.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)
- [ThreatConnect](../solutions/threatconnect.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md)

---

## Content Items Using This Table (58)

### Analytic Rules (31)

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
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntIp.yaml)

**In solution [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md):**
- [GreyNoise TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_imNetworkSession.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Possible Phishing with CSL and Network Sessions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/PossiblePhishingwithCSL%26NetworkSession.yaml)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [Anomaly found in Network Session Traffic (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/AnomalyFoundInNetworkSessionTraffic.yaml)
- [Anomaly in SMB Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/Anomaly%20in%20SMB%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)
- [Detect port misuse by anomaly based detection (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/DetectPortMisuseByAnomalyBasedDetection.yaml)
- [Detect port misuse by static threshold (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/DetectPortMisuseByStaticThreshold.yaml)
- [Excessive number of failed connections from a single source (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/ExcessiveHTTPFailuresFromSource.yaml)
- [Network Port Sweep from External Network (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/NetworkPortSweepFromExternalNetwork.yaml)
- [Port scan detected  (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/PortScan.yaml)
- [Potential beaconing activity (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/PossibleBeaconingActivity.yaml)
- [Remote Desktop Network Brute force (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/Remote%20Desktop%20Network%20Brute%20force%20%28ASIM%20Network%20Session%20schema%29.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingDomainAllActors.yaml)
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingIPAllActors.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml)
- [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml)
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imNetworkSession.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml)
- [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml)
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imNetworkSession.yaml)

**In solution [ThreatConnect](../solutions/threatconnect.md):**
- [ThreatConnect TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_IPEntity_NetworkSessions.yaml)

### Hunting Queries (21)

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
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntIp.yaml)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [Detect Outbound LDAP Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Detect%20Outbound%20LDAP%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)
- [Detect port misuse by anomaly (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectPortMisuseByAnomalyHunting.yaml)
- [Detect port misuse by static threshold (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectPortMisuseByStaticThresholdHunting.yaml)
- [Detects several users with the same MAC address (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectsSeveralUsersWithTheSameMACAddress.yaml)
- [Mismatch between Destination App name and Destination Port (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/MismatchBetweenDestinationAppNameAndDestinationPort.yaml)
- [Protocols passing authentication in cleartext (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Protocols%20passing%20authentication%20in%20cleartext%20%28ASIM%20Network%20Session%20schema%29.yaml)
- [Remote Desktop Network Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Remote%20Desktop%20Network%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureDomainThreatActorHunt.yaml)
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureIPThreatActorHunt.yaml)

### Workbooks (4)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [DNSSolutionWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Workbooks/DNSSolutionWorkbook.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [NetworkSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentials.json)
- [NetworkSessionEssentialsV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentialsV2.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
