# Infoblox NIOS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-04-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Infoblox NIOS](../connectors/infobloxnios.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Infoblox`](../tables/infoblox.md) | - | Analytics |
| [`Infoblox_dhcp_consolidated`](../tables/infoblox-dhcp-consolidated.md) | - | Workbooks |
| [`Infoblox_dns_consolidated`](../tables/infoblox-dns-consolidated.md) | - | Workbooks |
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Infoblox NIOS](../connectors/infobloxnios.md) | Analytics, Workbooks |

## Content Items

This solution includes **26 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 22 |
| Analytic Rules | 2 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Excessive NXDOMAIN DNS Queries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Analytic%20Rules/ExcessiveNXDOMAINDNSQueries.yaml) | Medium | CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [Potential DHCP Starvation Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Analytic%20Rules/PotentialDHCPStarvationAttack.yaml) | Medium | InitialAccess | [`Infoblox`](../tables/infoblox.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Infoblox-Workbook-V2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Workbooks/Infoblox-Workbook-V2.json) | [`Infoblox_dhcp_consolidated`](../tables/infoblox-dhcp-consolidated.md)<br>[`Infoblox_dns_consolidated`](../tables/infoblox-dns-consolidated.md)<br>[`Syslog`](../tables/syslog.md) |
| [Sources_by_SourceType](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Workbooks/Sources_by_SourceType.json) | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Infoblox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox.yaml) | - | - |
| [Infoblox_allotherdhcpdTypes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_allotherdhcpdTypes.yaml) | - | - |
| [Infoblox_allotherdnsTypes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_allotherdnsTypes.yaml) | - | - |
| [Infoblox_allotherlogTypes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_allotherlogTypes.yaml) | - | - |
| [Infoblox_dhcp_consolidated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcp_consolidated.yaml) | - | - |
| [Infoblox_dhcpack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpack.yaml) | - | - |
| [Infoblox_dhcpadded](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpadded.yaml) | - | - |
| [Infoblox_dhcpbindupdate](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpbindupdate.yaml) | - | - |
| [Infoblox_dhcpdiscover](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpdiscover.yaml) | - | - |
| [Infoblox_dhcpexpire](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpexpire.yaml) | - | - |
| [Infoblox_dhcpinform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpinform.yaml) | - | - |
| [Infoblox_dhcpoffer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpoffer.yaml) | - | - |
| [Infoblox_dhcpoption](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpoption.yaml) | - | - |
| [Infoblox_dhcpother](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpother.yaml) | - | - |
| [Infoblox_dhcprelease](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcprelease.yaml) | - | - |
| [Infoblox_dhcpremoved](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpremoved.yaml) | - | - |
| [Infoblox_dhcprequest](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcprequest.yaml) | - | - |
| [Infoblox_dhcpsession](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dhcpsession.yaml) | - | - |
| [Infoblox_dns_consolidated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dns_consolidated.yaml) | - | - |
| [Infoblox_dnsclient](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dnsclient.yaml) | - | - |
| [Infoblox_dnsgss](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dnsgss.yaml) | - | - |
| [Infoblox_dnszone](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Parsers/Infoblox_dnszone.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                   |
|-------------|--------------------------------|----------------------------------------------------------------------|
| 3.0.5       | 07-10-2025                     |Expanded exclusion lists in Infoblox_allotherdhcpdTypes and Infoblox_dhcpother parsers to filter additional log types.                   |
| 3.0.4       | 17-12-2024                     |Removed Deprecated **Data connectors**                                |
| 3.0.3       | 01-08-2024                     |Update **Parser** as part of Syslog migration                         |
|             |                                |Deprecating data connectors                                           |
| 3.0.2       | 16-08-2023                     |Updated the solution to include a default value for watchlist1-id     |
| 3.0.1       | 24-07-2023                     |Updated ApiVersion for Watchlist                                      |
| 3.0.0       | 11-07-2023                     |Updated support information for this solution                         |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
