# Web Session Essentials

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **10 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md) | Analytics, Hunting, Playbooks, Workbooks |
| [`AZFWApplicationRule`](../tables/azfwapplicationrule.md) | Analytics, Hunting, Playbooks, Workbooks |
| [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) | Analytics, Hunting, Playbooks, Workbooks |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Analytics, Hunting, Playbooks, Workbooks |
| [`SquidProxy_CL`](../tables/squidproxy-cl.md) | Analytics, Hunting, Playbooks, Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | Workbooks |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | Analytics, Hunting, Playbooks, Workbooks |
| [`W3CIISLog`](../tables/w3ciislog.md) | Analytics, Hunting, Playbooks, Workbooks |
| [`barracuda_CL`](../tables/barracuda-cl.md) | Analytics, Hunting, Playbooks, Workbooks |
| [`meraki_CL`](../tables/meraki-cl.md) | Analytics, Hunting, Playbooks, Workbooks |

### Internal Tables

The following **5 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | Workbooks |
| [`WebSession_Summarized_DstIP_CL`](../tables/websession-summarized-dstip-cl.md) | Playbooks (writes), Workbooks |
| [`WebSession_Summarized_SrcIP_CL`](../tables/websession-summarized-srcip-cl.md) | Analytics, Playbooks (writes), Workbooks |
| [`WebSession_Summarized_SrcInfo_CL`](../tables/websession-summarized-srcinfo-cl.md) | Analytics, Playbooks (writes), Workbooks |
| [`WebSession_Summarized_ThreatInfo_CL`](../tables/websession-summarized-threatinfo-cl.md) | Playbooks (writes), Workbooks |

## Content Items

This solution includes **26 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 15 |
| Hunting Queries | 9 |
| Workbooks | 1 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Detect Local File Inclusion(LFI) in web requests (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/LocalFileInclusion-LFI.yaml) | High | InitialAccess, Execution | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect URLs containing known malicious keywords or commands (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/CommandInURL.yaml) | High | InitialAccess, CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect instances of multiple client errors occurring within a brief period of time (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/MultipleClientErrorsWithinShortTime.yaml) | Medium | InitialAccess, CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect instances of multiple server errors occurring within a brief period of time (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/MultipleServerErrorsWithinShortTime.yaml) | Medium | InitialAccess, Impact | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect known risky user agents (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/KnownMaliciousUserAgents.yaml) | Medium | InitialAccess, CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect potential file enumeration activity (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/PotentionalFileEnumeration.yaml) | Medium | Discovery, CommandAndControl, CredentialAccess | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect potential presence of a malicious file with a double extension (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/PossibleMaliciousDoubleExtension.yaml) | Medium | DefenseEvasion, Persistence, CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect presence of private IP addresses in URLs (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/PrivateIPInURL.yaml) | Medium | Exfiltration, CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect presence of uncommon user agents in web requests (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/RareUserAgentDetected.yaml) | Medium | InitialAccess | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>*Internal use:*<br>[`WebSession_Summarized_SrcInfo_CL`](../tables/websession-summarized-srcinfo-cl.md) |
| [Detect requests for an uncommon resources on the web (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/RarelyRequestedResources.yaml) | Low | CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect threat information in web requests (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/ThreatInfoFoundInWebRequests.yaml) | High | InitialAccess | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect unauthorized data transfers using timeseries anomaly (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/DataExfiltrationTimeSeriesAnomaly.yaml) | Medium | Exfiltration | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>*Internal use:*<br>[`WebSession_Summarized_SrcIP_CL`](../tables/websession-summarized-srcip-cl.md) |
| [Detect web requests to potentially harmful files (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/RequestToPotentiallyHarmfulFileTypes.yaml) | Medium | InitialAccess, Persistence, Execution | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Identify instances where a single source is observed using multiple user agents (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/MultipleUAsFromSingleIP.yaml) | Medium | InitialAccess, CredentialAccess | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [The download of potentially risky files from the Discord Content Delivery Network (CDN) (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Analytic%20Rules/DiscordCDNRiskyFileDownload.yaml) | Medium | CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Beaconing traffic based on common user agents visiting limited number of domains (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/PotentialBeaconingDetected_LimitedDomainBased.yaml) | CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect IPAddress in the requested URL (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/IPAddressInURL.yaml) | Exfiltration, CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect Kali Linux UserAgent (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/KaliLinuxUserAgentDetected.yaml) | Execution | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Detect threat information in web requests (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/ThreatInfoFoundInWebRequests.yaml) | InitialAccess | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Empty User Agent Detected (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/EmptyUserAgent.yaml) | InitialAccess | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Excessive number of forbidden requests detected (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/ExcessiveForbiddenRequestsDetected.yaml) | Persistence, CredentialAccess | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Potential beaconing detected (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/PotentialBeaconingDetected_TimeDelta.yaml) | CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Potential beaconing detected - Similar sent bytes (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/PotentialBeaconingDetected_SimilarSrcBytes.yaml) | CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Request from bots and crawlers (ASIM Web Session)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Hunting%20Queries/RequestFromBotsAndCrawlers.yaml) | InitialAccess | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [WebSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Workbooks/WebSessionEssentials.json) | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`WebSession_Summarized_DstIP_CL`](../tables/websession-summarized-dstip-cl.md)<br>[`WebSession_Summarized_SrcIP_CL`](../tables/websession-summarized-srcip-cl.md)<br>[`WebSession_Summarized_SrcInfo_CL`](../tables/websession-summarized-srcinfo-cl.md)<br>[`WebSession_Summarized_ThreatInfo_CL`](../tables/websession-summarized-threatinfo-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Summarize Web Session Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Playbooks/SummarizeWebSessionData/azuredeploy.json) | The 'SummarizeWebSessionData' Playbook helps with summarizing the Web Session logs and ingesting the... | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md) *(read)*<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md) *(read)*<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) *(read)*<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md) *(read)*<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md) *(read)*<br>[`VectraStream_CL`](../tables/vectrastream-cl.md) *(read)*<br>[`W3CIISLog`](../tables/w3ciislog.md) *(read)*<br>[`barracuda_CL`](../tables/barracuda-cl.md) *(read)*<br>[`meraki_CL`](../tables/meraki-cl.md) *(read)*<br>*Internal use:*<br>[`WebSession_Summarized_DstIP_CL`](../tables/websession-summarized-dstip-cl.md) *(read/write)*<br>[`WebSession_Summarized_SrcIP_CL`](../tables/websession-summarized-srcip-cl.md) *(write)*<br>[`WebSession_Summarized_SrcInfo_CL`](../tables/websession-summarized-srcinfo-cl.md) *(write)*<br>[`WebSession_Summarized_ThreatInfo_CL`](../tables/websession-summarized-threatinfo-cl.md) *(write)* |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                            |
|-------------|--------------------------------|-----------------------------------------------|
| 3.0.3       | 06-06-2024                     | Updated Entity Mapping **Analytic Rule** CommandInURL.yaml 	                       |
| 3.0.2       | 31-01-2024                     | Updated the solution to fix **Analytic Rules** deployment issue     |
| 3.0.1       | 02-01-2024                     | Tagged for dependent Solutions for deployment |
| 3.0.0       | 11-09-2023                     | Initial Solution Release                      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
