# SonicWall Firewall

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SonicWall |
| **Support Tier** | Partner |
| **Support Link** | [https://www.sonicwall.com/support/](https://www.sonicwall.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] SonicWall Firewall via Legacy Agent](../connectors/sonicwallfirewall.md)

**Publisher:** SonicWall

Common Event Format (CEF) is an industry standard format on top of Syslog messages, used by SonicWall to allow event interoperability among different platforms. By connecting your CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [SonicwallFirewall.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall/Data%20Connectors/SonicwallFirewall.json) |

[→ View full connector details](../connectors/sonicwallfirewall.md)

### [[Deprecated] SonicWall Firewall via AMA](../connectors/sonicwallfirewallama.md)

**Publisher:** SonicWall

Common Event Format (CEF) is an industry standard format on top of Syslog messages, used by SonicWall to allow event interoperability among different platforms. By connecting your CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_SonicwallFirewallAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall/Data%20Connectors/template_SonicwallFirewallAMA.json) |

[→ View full connector details](../connectors/sonicwallfirewallama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] SonicWall Firewall via AMA](../connectors/sonicwallfirewallama.md), [[Deprecated] SonicWall Firewall via Legacy Agent](../connectors/sonicwallfirewall.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.1.2       | 28-11-2024                     |    Removed Deprecated **Data Connectors**                          |
| 3.1.1       | 27-06-2024                     |	OMS Data Connector Migration                                    |
| 3.1.0       | 29-03-2024                     |	Addition of new content, including ASIM Network Session and Web Session parsers, Analytic Rules, Hunting Queries, and a Workbook.     |
| 3.0.0       | 18-09-2023                     |	Addition of new SonicWall Firewall AMA **Data Connector**     |

[← Back to Solutions Index](../solutions-index.md)
