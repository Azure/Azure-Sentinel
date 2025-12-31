# W3CIISLog

Reference for W3CIISLog table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | IT & Management Tools, Virtual Machines |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/w3ciislog) |

## Solutions (10)

This table is used by the following solutions:

- [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md)
- [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md)
- [Recorded Future](../solutions/recorded-future.md)
- [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)
- [Web Session Essentials](../solutions/web-session-essentials.md)
- [Web Shells Threat Protection](../solutions/web-shells-threat-protection.md)

## Connectors (2)

This table is ingested by the following connectors:

- [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md)
- [IIS Logs of Microsoft Exchange Servers](../connectors/esi-opt5exchangeiislogs.md)

---

## Content Items Using This Table (44)

### Analytic Rules (28)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [Log4j vulnerability exploit aka Log4Shell IP IOC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/Log4J_IPIOC_Dec112021.yaml)
- [User agent search for log4j exploitation attempt](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/UserAgentSearch_log4j.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntUrl.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Url All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingUrlAllActors.yaml)

**In solution [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md):**
- [Possible AiTM Phishing Attempt Against Microsoft Entra ID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/PossibleAiTMPhishingAttemptAgainstAAD.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI Map IP Entity to W3CIISLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_W3CIISLog.yaml)
- [TI map Domain entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_imWebSession.yaml)
- [TI map IP entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imWebSession.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI Map IP Entity to W3CIISLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_W3CIISLog.yaml)
- [TI map Domain entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_imWebSession.yaml)
- [TI map IP entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imWebSession.yaml)

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

**In solution [Web Shells Threat Protection](../solutions/web-shells-threat-protection.md):**
- [Malicious web application requests linked with Microsoft Defender for Endpoint (formerly Microsoft Defender ATP) alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Analytic%20Rules/MaliciousAlertLinkedWebRequests.yaml)
- [SUPERNOVA webshell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Analytic%20Rules/Supernovawebshell.yaml)

### Hunting Queries (13)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntUrl.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
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

**In solution [Web Shells Threat Protection](../solutions/web-shells-threat-protection.md):**
- [Web Shell Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/WebShellActivity.yaml)
- [Webshell Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/PotentialWebshell.yaml)

### Workbooks (2)

**In solution [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md):**
- [GDPRComplianceAndDataSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json)

**In solution [Web Session Essentials](../solutions/web-session-essentials.md):**
- [WebSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Workbooks/WebSessionEssentials.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.compute/virtualmachines`
- `microsoft.conenctedvmwarevsphere/virtualmachines`
- `microsoft.azurestackhci/virtualmachines`
- `microsoft.scvmm/virtualmachines`
- `microsoft.compute/virtualmachinescalesets`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
