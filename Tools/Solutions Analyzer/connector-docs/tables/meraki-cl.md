# meraki_CL

## Solutions (15)

This table is used by the following solutions:

- [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md)
- [CiscoMeraki](../solutions/ciscomeraki.md)
- [CustomLogsAma](../solutions/customlogsama.md)
- [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Network Session Essentials](../solutions/network-session-essentials.md)
- [Recorded Future](../solutions/recorded-future.md)
- [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)
- [ThreatConnect](../solutions/threatconnect.md)
- [Web Session Essentials](../solutions/web-session-essentials.md)

## Connectors (4)

This table is ingested by the following connectors:

- [[Deprecated] Cisco Meraki](../connectors/ciscomeraki.md)
- [Cisco Meraki (using REST API)](../connectors/ciscomeraki%28usingrestapi%29.md)
- [Cisco Meraki (using REST API)](../connectors/ciscomerakinativepoller.md)
- [Custom logs via AMA](../connectors/customlogsviaama.md)

---

## Content Items Using This Table (67)

### Analytic Rules (39)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [User agent search for log4j exploitation attempt](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/UserAgentSearch_log4j.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntIp.yaml)
- [Google Threat Intelligence - Threat Hunting Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntUrl.yaml)

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
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingIPAllActors.yaml)
- [RecordedFuture Threat Hunting Url All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingUrlAllActors.yaml)

**In solution [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md):**
- [Possible AiTM Phishing Attempt Against Microsoft Entra ID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/PossibleAiTMPhishingAttemptAgainstAAD.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map Domain entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_imWebSession.yaml)
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imNetworkSession.yaml)
- [TI map IP entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imWebSession.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map Domain entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_imWebSession.yaml)
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imNetworkSession.yaml)
- [TI map IP entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imWebSession.yaml)

**In solution [ThreatConnect](../solutions/threatconnect.md):**
- [ThreatConnect TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_IPEntity_NetworkSessions.yaml)

**In solution [Web Session Essentials](../solutions/web-session-essentials.md):**
- [Detect Local File Inclusion(LFI) in web requests (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/LocalFileInclusion-LFI.yaml)
- [Detect URLs containing known malicious keywords or commands (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/CommandInURL.yaml)
- [Detect instances of multiple client errors occurring within a brief period of time (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/MultipleClientErrorsWithinShortTime.yaml)
- [Detect instances of multiple server errors occurring within a brief period of time (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/MultipleServerErrorsWithinShortTime.yaml)
- [Detect known risky user agents (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/KnownMaliciousUserAgents.yaml)
- [Detect potential file enumeration activity (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/PotentionalFileEnumeration.yaml)
- [Detect potential presence of a malicious file with a double extension (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/PossibleMaliciousDoubleExtension.yaml)
- [Detect presence of private IP addresses in URLs (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/PrivateIPInURL.yaml)
- [Detect presence of uncommon user agents in web requests (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/RareUserAgentDetected.yaml)
- [Detect requests for an uncommon resources on the web (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/RarelyRequestedResources.yaml)
- [Detect threat information in web requests (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/ThreatInfoFoundInWebRequests.yaml)
- [Detect unauthorized data transfers using timeseries anomaly (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/DataExfiltrationTimeSeriesAnomaly.yaml)
- [Detect web requests to potentially harmful files (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/RequestToPotentiallyHarmfulFileTypes.yaml)
- [Identify instances where a single source is observed using multiple user agents (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/MultipleUAsFromSingleIP.yaml)
- [The download of potentially risky files from the Discord Content Delivery Network (CDN) (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/DiscordCDNRiskyFileDownload.yaml)

### Hunting Queries (20)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntIp.yaml)
- [Google Threat Intelligence - Threat Hunting Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntUrl.yaml)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [Detect Outbound LDAP Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Detect%20Outbound%20LDAP%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)
- [Detect port misuse by anomaly (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectPortMisuseByAnomalyHunting.yaml)
- [Detect port misuse by static threshold (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectPortMisuseByStaticThresholdHunting.yaml)
- [Detects several users with the same MAC address (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectsSeveralUsersWithTheSameMACAddress.yaml)
- [Mismatch between Destination App name and Destination Port (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/MismatchBetweenDestinationAppNameAndDestinationPort.yaml)
- [Protocols passing authentication in cleartext (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Protocols%20passing%20authentication%20in%20cleartext%20%28ASIM%20Network%20Session%20schema%29.yaml)
- [Remote Desktop Network Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Remote%20Desktop%20Network%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureIPThreatActorHunt.yaml)
- [RecordedFuture Threat Hunting URL All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureUrlThreatActorHunt.yaml)

**In solution [Web Session Essentials](../solutions/web-session-essentials.md):**
- [Beaconing traffic based on common user agents visiting limited number of domains (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/PotentialBeaconingDetected_LimitedDomainBased.yaml)
- [Detect IPAddress in the requested URL (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/IPAddressInURL.yaml)
- [Detect Kali Linux UserAgent (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/KaliLinuxUserAgentDetected.yaml)
- [Detect threat information in web requests (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/ThreatInfoFoundInWebRequests.yaml)
- [Empty User Agent Detected (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/EmptyUserAgent.yaml)
- [Excessive number of forbidden requests detected (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/ExcessiveForbiddenRequestsDetected.yaml)
- [Potential beaconing detected (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/PotentialBeaconingDetected_TimeDelta.yaml)
- [Potential beaconing detected - Similar sent bytes (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/PotentialBeaconingDetected_SimilarSrcBytes.yaml)
- [Request from bots and crawlers (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/RequestFromBotsAndCrawlers.yaml)

### Workbooks (6)

**In solution [CiscoMeraki](../solutions/ciscomeraki.md):**
- [CiscoMerakiWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Workbooks/CiscoMerakiWorkbook.json)

**In solution [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md):**
- [GDPRComplianceAndDataSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [NetworkSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentials.json)
- [NetworkSessionEssentialsV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentialsV2.json)

**In solution [Web Session Essentials](../solutions/web-session-essentials.md):**
- [WebSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Workbooks/WebSessionEssentials.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
