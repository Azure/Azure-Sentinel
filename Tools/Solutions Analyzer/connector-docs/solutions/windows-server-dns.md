# Windows Server DNS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Windows DNS Events via AMA](../connectors/asimdnsactivitylogs.md)
- [DNS](../connectors/dns.md)

## Tables Reference

This solution uses **6 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md) | [Windows DNS Events via AMA](../connectors/asimdnsactivitylogs.md) | - |
| [`DnsEvents`](../tables/dnsevents.md) | [DNS](../connectors/dns.md) | Analytics, Hunting, Workbooks |
| [`DnsInventory`](../tables/dnsinventory.md) | [DNS](../connectors/dns.md) | Workbooks |
| [`FilterOnIPThreshold_MainTable`](../tables/filteronipthreshold-maintable.md) | - | Hunting |
| [`SigninLogs`](../tables/signinlogs.md) | - | Hunting |
| [`quartileFunctionForIPThreshold`](../tables/quartilefunctionforipthreshold.md) | - | Hunting |

## Content Items

This solution includes **15 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 9 |
| Analytic Rules | 5 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [DNS events related to ToR proxies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Analytic%20Rules/DNS_TorProxies.yaml) | Low | Exfiltration | [`DnsEvents`](../tables/dnsevents.md) |
| [DNS events related to mining pools](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Analytic%20Rules/DNS_Miners.yaml) | Low | Impact | [`DnsEvents`](../tables/dnsevents.md) |
| [NRT DNS events related to mining pools](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Analytic%20Rules/NRT_DNS_Related_To_Mining_Pools.yaml) | Low | Impact | [`DnsEvents`](../tables/dnsevents.md) |
| [Potential DGA detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Analytic%20Rules/DNS_HighNXDomainCount_detection.yaml) | Medium | CommandAndControl | [`DnsEvents`](../tables/dnsevents.md) |
| [Rare client observed with high reverse DNS lookup count](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Analytic%20Rules/DNS_HighReverseDNSCount_detection.yaml) | Medium | Discovery | [`DnsEvents`](../tables/dnsevents.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Abnormally long DNS URI queries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Hunting%20Queries/DNS_LongURILookup.yaml) | CommandAndControl, Exfiltration | [`DnsEvents`](../tables/dnsevents.md) |
| [DNS - domain anomalous lookup increase](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Hunting%20Queries/DNS_DomainAnomalousLookupIncrease.yaml) | CommandAndControl, Exfiltration | [`DnsEvents`](../tables/dnsevents.md) |
| [DNS Domains linked to WannaCry ransomware campaign](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Hunting%20Queries/DNS_WannaCry.yaml) | Impact | [`DnsEvents`](../tables/dnsevents.md) |
| [DNS Full Name anomalous lookup increase](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Hunting%20Queries/DNS_FullNameAnomalousLookupIncrease.yaml) | CommandAndControl, Exfiltration | [`DnsEvents`](../tables/dnsevents.md) |
| [DNS lookups for commonly abused TLDs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Hunting%20Queries/DNS_CommonlyAbusedTLDs.yaml) | CommandAndControl, Exfiltration | [`DnsEvents`](../tables/dnsevents.md) |
| [High reverse DNS count by host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Hunting%20Queries/DNS_HighReverseDNSCount.yaml) | Discovery | [`DnsEvents`](../tables/dnsevents.md) |
| [Potential DGA detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Hunting%20Queries/DNS_HighPercentNXDomainCount.yaml) | CommandAndControl | [`DnsEvents`](../tables/dnsevents.md)<br>[`FilterOnIPThreshold_MainTable`](../tables/filteronipthreshold-maintable.md)<br>[`quartileFunctionForIPThreshold`](../tables/quartilefunctionforipthreshold.md) |
| [Solorigate DNS Pattern](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Hunting%20Queries/Solorigate-DNS-Pattern.yaml) | CommandAndControl | [`DnsEvents`](../tables/dnsevents.md) |
| [Solorigate Encoded Domain in URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Hunting%20Queries/Solorigate-Encoded-Domain-URL.yaml) | CommandAndControl | [`SigninLogs`](../tables/signinlogs.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Dns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Workbooks/Dns.json) | [`DnsEvents`](../tables/dnsevents.md)<br>[`DnsInventory`](../tables/dnsinventory.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 19-03-2024                     | Updated Entity Mappings of **Analytic Rules**    										|	
| 3.0.0       | 18-09-2023                     | Windows DNS Events via AMA **Data Connector** now General Availability   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
