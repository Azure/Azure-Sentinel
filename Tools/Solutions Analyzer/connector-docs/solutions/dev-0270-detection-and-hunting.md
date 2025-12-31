# Dev 0270 Detection and Hunting

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-11-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dev%200270%20Detection%20and%20Hunting](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dev%200270%20Detection%20and%20Hunting) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [DEV-0270 New User Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dev%200270%20Detection%20and%20Hunting/Analytic%20Rules/Dev-0270NewUserSep2022.yaml) | High | Persistence | - |
| [Dev-0270 Malicious Powershell usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dev%200270%20Detection%20and%20Hunting/Analytic%20Rules/Dev-0270PowershellSep2022.yaml) | High | Exfiltration, DefenseEvasion | - |
| [Dev-0270 Registry IOC - September 2022](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dev%200270%20Detection%20and%20Hunting/Analytic%20Rules/Dev-0270RegistryIOCSep2022.yaml) | High | Impact | - |
| [Dev-0270 WMIC  Discovery](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dev%200270%20Detection%20and%20Hunting/Analytic%20Rules/Dev-0270WMICDiscoverySep2022.yaml) | High | Discovery | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 07-06-2024                     |	Added missing AMA **Data Connector** reference in **Analytic Rule** |  
| 3.0.0       | 12-04-2024                     |	Updated Entity Mappings of **Analytic Rule**                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
