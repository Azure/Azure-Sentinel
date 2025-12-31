# Ubiquiti UniFi

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Ubiquiti UniFi](../connectors/ubiquitiunifi.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | - | Analytics |
| [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) | [[Deprecated] Ubiquiti UniFi](../connectors/ubiquitiunifi.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **22 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Ubiquiti - Connection to known malicious IP or C2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiDestinationInTiList.yaml) | Medium | Exfiltration, CommandAndControl | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [Ubiquiti - Large ICMP to external server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiL2RLargeIcmp.yaml) | Medium | Exfiltration, CommandAndControl | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Possible connection to cryptominning pool](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiCryptominer.yaml) | Medium | CommandAndControl | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - RDP from external source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiR2LRDP.yaml) | Medium | InitialAccess | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - SSH from external source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiR2LSSH.yaml) | Medium | InitialAccess | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Unknown MAC Joined AP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiUnknownMacJoined.yaml) | Medium | InitialAccess | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Unusual DNS connection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiR2LDns.yaml) | Medium | CommandAndControl | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Unusual FTP connection to external server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiL2RFTP.yaml) | Medium | Exfiltration, CommandAndControl | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Unusual traffic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiUnusualTraffic.yaml) | Medium | CommandAndControl | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - connection to non-corporate DNS server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiNonCorpDns.yaml) | Medium | CommandAndControl, Exfiltration | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Ubiquiti - DNS requests timed out](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Hunting%20Queries/UbiquitiDnsTimeOut.yaml) | CommandAndControl, Exfiltration | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Hidden internal DNS server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Hunting%20Queries/UbiquitiInternalDnsServer.yaml) | CommandAndControl | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Rare internal ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Hunting%20Queries/UbiquitiRareInternalPorts.yaml) | CommandAndControl | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Top blocked destinations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Hunting%20Queries/UbiquitiTopBlockedDst.yaml) | CommandAndControl, Exfiltration | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Top blocked external services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Hunting%20Queries/UbiquitiTopBlockedExternalServices.yaml) | CommandAndControl, Exfiltration | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Top blocked internal services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Hunting%20Queries/UbiquitiTopBlockedInternalServices.yaml) | InitialAccess, CommandAndControl | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Top blocked sources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Hunting%20Queries/UbiquitiTopBlockedSrc.yaml) | CommandAndControl, Exfiltration | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Top firewall rules](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Hunting%20Queries/UbiquitiTopFirewallRules.yaml) | CommandAndControl, Exfiltration | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Unusual number of subdomains for top level domain (TLD)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Hunting%20Queries/UbiquitiUnusualSubdomains.yaml) | CommandAndControl | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |
| [Ubiquiti - Vulnerable devices](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Hunting%20Queries/UbiquitiVulnerableDevices.yaml) | InitialAccess | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Ubiquiti](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Workbooks/Ubiquiti.json) | [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [UbiquitiAuditEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Parsers/UbiquitiAuditEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                        |
|-------------|--------------------------------|---------------------------------------------------------------------------|
| 3.0.3       | 04-12-2024                     | Removed Deprecated **Data Connector**                                     |
| 3.0.2       | 09-08-2024                     | Deprecating data connectors                                               |
| 3.0.1       | 16-07-2024                     | Updated the **Analytic rules** for missing TTP					   		   |
| 3.0.0       | 23-01-2024                     | Updated the **Data Connector** by removing preview-tag   				   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
