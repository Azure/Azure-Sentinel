# SonicWall Firewall

## Solution Information

| | |
|------------------------|-------|
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

### [[Deprecated] SonicWall Firewall via AMA](../connectors/sonicwallfirewallama.md)

**Publisher:** SonicWall

Common Event Format (CEF) is an industry standard format on top of Syslog messages, used by SonicWall to allow event interoperability among different platforms. By connecting your CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_SonicwallFirewallAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall/Data%20Connectors/template_SonicwallFirewallAMA.json) |

[→ View full connector details](../connectors/sonicwallfirewallama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] SonicWall Firewall via AMA](../connectors/sonicwallfirewallama.md), [[Deprecated] SonicWall Firewall via Legacy Agent](../connectors/sonicwallfirewall.md) |

[← Back to Solutions Index](../solutions-index.md)
