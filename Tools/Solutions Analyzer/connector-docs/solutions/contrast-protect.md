# Contrast Protect

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Contrast Protect |
| **Support Tier** | Partner |
| **Support Link** | [https://docs.contrastsecurity.com/](https://docs.contrastsecurity.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Contrast Protect via Legacy Agent](../connectors/contrastprotect.md)
- [[Deprecated] Contrast Protect via AMA](../connectors/contrastprotectama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Contrast Protect via AMA](../connectors/contrastprotectama.md), [[Deprecated] Contrast Protect via Legacy Agent](../connectors/contrastprotect.md) | Analytics, Workbooks |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Contrast Blocks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Analytic%20Rules/ContrastBlocks.yaml) | Low | InitialAccess, Exfiltration | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Contrast Exploits](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Analytic%20Rules/ContrastExploits.yaml) | High | InitialAccess, Exfiltration | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Contrast Probes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Analytic%20Rules/ContrastProbes.yaml) | Informational | InitialAccess, Exfiltration | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Contrast Suspicious](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Analytic%20Rules/ContrastSuspicious.yaml) | Medium | InitialAccess, Exfiltration | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ContrastProtect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Workbooks/ContrastProtect.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 11-07-2024                     |    Deprecating data connectors                                     |
| 3.0.0       | 07-09-2023                     |	Addition of new Contrast Protect AMA **Data Connector**         |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
