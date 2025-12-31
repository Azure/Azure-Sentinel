# Fortinet FortiWeb Cloud WAF-as-a-Service connector for Microsoft Sentinel

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Fortinet FortiWeb Web Application Firewall via Legacy Agent](../connectors/fortinetfortiweb.md)
- [Fortinet FortiWeb Web Application Firewall via AMA](../connectors/fortinetfortiwebama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [Fortinet FortiWeb Web Application Firewall via AMA](../connectors/fortinetfortiwebama.md), [[Deprecated] Fortinet FortiWeb Web Application Firewall via Legacy Agent](../connectors/fortinetfortiweb.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **7 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 2 |
| Playbooks | 2 |
| Analytic Rules | 1 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Fortiweb - WAF Allowed threat](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Analytic%20Rules/Fortiweb%20-%20WAF%20Allowed%20threat.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Fortiweb - Unexpected countries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Hunting%20Queries/Unexpected%20Countries.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Fortiweb - identify owasp10 vulnerabilities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Hunting%20Queries/owaspTop10-Threatsyaml.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Fortiweb-workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Workbooks/Fortiweb-workbook.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Block IP & URL on fortiweb cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Playbooks/FortiWebPlaybooks/FortiWeb-BlockIP-URL/azuredeploy.json) | This Playbook Provides the automation on blocking the suspicious/malicious IP and URL on fortiweb cl... | - |
| [Fetch Threat Intel from fortiwebcloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Playbooks/FortiWebPlaybooks/FortiWeb-enrichment/azuredeploy.json) | This playbook provides/updates the threat intel and essential details in comments section of trigger... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Fortiweb](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Parsers/Fortiweb.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                | 
|-------------|--------------------------------|-------------------------------------------------------------------|
| 3.0.3       | 10-12-2024                     | Removed Deprecated **Data Connectors**                            |
| 3.0.2       | 30-04-2024                     | Repackaged for parser issue fix on reinstall                      |
| 3.0.1       | 26-02-2024                     |Addition of new Fortinet FortiWeb Cloud WAF AMA **Data Connector** |
| 3.0.0       | 11-07-2023                     |Updated the title and the description of the solution              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
