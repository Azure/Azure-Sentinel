# Web Shells Threat Protection

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-22 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **5 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Hunting |
| [`DeviceFileEvents`](../tables/devicefileevents.md) | Hunting |
| [`SecurityEvent`](../tables/securityevent.md) | Analytics |
| [`W3CIISLog`](../tables/w3ciislog.md) | Analytics, Hunting |
| [`false`](../tables/false.md) | Hunting |

## Content Items

This solution includes **9 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 6 |
| Analytic Rules | 3 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Identify SysAid Server web shell creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Analytic%20Rules/PotentialMercury_Webshell.yaml) | High | InitialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [Malicious web application requests linked with Microsoft Defender for Endpoint (formerly Microsoft Defender ATP) alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Analytic%20Rules/MaliciousAlertLinkedWebRequests.yaml) | Medium | Persistence | [`W3CIISLog`](../tables/w3ciislog.md) |
| [SUPERNOVA webshell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Analytic%20Rules/Supernovawebshell.yaml) | High | Persistence, CommandAndControl | [`W3CIISLog`](../tables/w3ciislog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Exchange IIS Worker Dropping Webshells](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/exchange-iis-worker-dropping-webshell.yaml) | Execution, Persistence | [`DeviceFileEvents`](../tables/devicefileevents.md) |
| [Possible Webshell usage attempt related to SpringShell(CVE-2022-22965)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/SpringshellWebshellUsage.yaml) | Execution | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Possible webshell drop](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/Possible%20webshell%20drop.yaml) | Initial access, Execution, Persistence | [`DeviceFileEvents`](../tables/devicefileevents.md)<br>[`false`](../tables/false.md) |
| [UMWorkerProcess Creating Webshell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/umworkerprocess-creating-webshell.yaml) | Execution, Persistence, Exploit | [`DeviceFileEvents`](../tables/devicefileevents.md) |
| [Web Shell Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/WebShellActivity.yaml) | Persistence, InitialAccess | [`W3CIISLog`](../tables/w3ciislog.md) |
| [Webshell Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/PotentialWebshell.yaml) | Persistence, PrivilegeEscalation | [`W3CIISLog`](../tables/w3ciislog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                            |
|-------------|--------------------------------|-------------------------------------------------------------------------------|
| 3.0.4       | 10-06-2024                     | Added missing AMA **Data Connector** reference in **Analytic rules**     |
| 3.0.3       | 12-04-2024                     | Updated Entity Mapping and Query of **Analytic Rule** Supernovawebshell.yaml and MaliciousAlertLinkedWebRequests.yaml                              |
| 3.0.2       | 22-02-2024                     | Tagged for dependent Solutions for deployment                                 |
| 3.0.1       | 25-10-2023                     | Changes for rebranding from Microsoft 365 Defender to Microsoft Defender XDR  |      
| 3.0.0       | 12-07-2023                     | Updated **Hunting Queries** descriptions to meet the 255 character limit.     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
