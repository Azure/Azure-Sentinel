# Network Threat Protection Essentials

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-11-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Threat%20Protection%20Essentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Threat%20Protection%20Essentials) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **2 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Hunting |
| [`UserAgentAll`](../tables/useragentall.md) | Analytics |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 3 |
| Analytic Rules | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Network endpoint to host executable correlation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Threat%20Protection%20Essentials/Analytic%20Rules/NetworkEndpointCorrelation.yaml) | Medium | Execution | - |
| [New UserAgent observed in last 24 hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Threat%20Protection%20Essentials/Analytic%20Rules/NewUserAgentLast24h.yaml) | Low | InitialAccess, CommandAndControl, Execution | [`UserAgentAll`](../tables/useragentall.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Base64 encoded IPv4 address in request url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Threat%20Protection%20Essentials/Hunting%20Queries/B64IPInURL.yaml) | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Exploit and Pentest Framework User Agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Threat%20Protection%20Essentials/Hunting%20Queries/UseragentExploitPentest.yaml) | InitialAccess, CommandAndControl, Execution | - |
| [Risky base64 encoded command in URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Threat%20Protection%20Essentials/Hunting%20Queries/RiskyCommandB64EncodedInUrl.yaml) | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                             |
|-------------|--------------------------------|--------------------------------------------------------------------------------|
| 3.0.1       | 23-02-2024                     | Tagged for dependent solutions for deployment                                  |
| 3.0.0       | 19-12-2023                     | Corrected typo mistake *Microsoft Windows DNS* to *Windows Server DNS*         |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
