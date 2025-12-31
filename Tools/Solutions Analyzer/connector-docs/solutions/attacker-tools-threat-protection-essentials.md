# Attacker Tools Threat Protection Essentials

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-11-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **2 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`DeviceProcessEvents`](../tables/deviceprocessevents.md) | Analytics |
| [`Event`](../tables/event.md) | Analytics |

## Content Items

This solution includes **6 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |
| Hunting Queries | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Credential Dumping Tools - File Artifacts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials/Analytic%20Rules/CredentialDumpingToolsFileArtifacts.yaml) | High | CredentialAccess | [`Event`](../tables/event.md) |
| [Credential Dumping Tools - Service Installation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials/Analytic%20Rules/CredentialDumpingServiceInstallation.yaml) | High | CredentialAccess | [`Event`](../tables/event.md) |
| [Powershell Empire Cmdlets Executed in Command Line](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials/Analytic%20Rules/powershell_empire.yaml) | Medium | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, LateralMovement, Persistence, PrivilegeEscalation | - |
| [Probable AdFind Recon Tool Usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials/Analytic%20Rules/AdFind_Usage.yaml) | High | Discovery | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Cobalt Strike DNS Beaconing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials/Hunting%20Queries/CobaltDNSBeacon.yaml) | CommandAndControl | - |
| [Potential Impacket Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials/Hunting%20Queries/PotentialImpacketExecution.yaml) | CredentialAccess | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                        |
|-------------|--------------------------------|---------------------------------------------------------------------------|
| 3.0.3       | 06-06-2024                     | Added missing AMA **Data Connector** reference in **Analytic rules** and **Hunting Queries**|
| 3.0.2       | 07-02-2024                     | Tagged for dependent solutions for deployment                             |
| 3.0.1       | 23-01-2024                     | Added subTechniques in Template                                           |
| 3.0.0       | 06-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
