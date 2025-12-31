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

This solution provides **2 data connector(s)**:

- [[Deprecated] SonicWall Firewall via Legacy Agent](../connectors/sonicwallfirewall.md)
- [[Deprecated] SonicWall Firewall via AMA](../connectors/sonicwallfirewallama.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] SonicWall Firewall via AMA](../connectors/sonicwallfirewallama.md), [[Deprecated] SonicWall Firewall via Legacy Agent](../connectors/sonicwallfirewall.md) | Analytics, Hunting, Workbooks |
| [`HighRiskPorts`](../tables/highriskports.md) | - | Workbooks |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |
| Hunting Queries | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [SonicWall - Allowed SSH, Telnet, and RDP Connections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall/Analytic%20Rules/AllowedInboundSSHTelnetRDPConnections.yaml) | Medium | InitialAccess, Execution, Persistence, CredentialAccess, Discovery, LateralMovement, Collection, Exfiltration, Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [SonicWall - Capture ATP Malicious File Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall/Analytic%20Rules/CaptureATPMaliciousFileDetection.yaml) | Medium | Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Outbound SSH/SCP Connections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall/Hunting%20Queries/OutboundSSHConnections.yaml) | Exfiltration | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SonicWallFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall/Workbooks/SonicWallFirewall.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`HighRiskPorts`](../tables/highriskports.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.1.2       | 28-11-2024                     |    Removed Deprecated **Data Connectors**                          |
| 3.1.1       | 27-06-2024                     |	OMS Data Connector Migration                                    |
| 3.1.0       | 29-03-2024                     |	Addition of new content, including ASIM Network Session and Web Session parsers, Analytic Rules, Hunting Queries, and a Workbook.     |
| 3.0.0       | 18-09-2023                     |	Addition of new SonicWall Firewall AMA **Data Connector**     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
