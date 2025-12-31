# Semperis Directory Services Protector

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Semperis |
| **Support Tier** | Partner |
| **Support Link** | [https://www.semperis.com/contact-us/](https://www.semperis.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Semperis Directory Services Protector](../connectors/semperisdsp.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | - | Workbooks |
| [`SecurityEvent`](../tables/securityevent.md) | [Semperis Directory Services Protector](../connectors/semperisdsp.md) | Analytics, Workbooks |

## Content Items

This solution includes **15 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 8 |
| Workbooks | 6 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Semperis DSP Failed Logons](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/Semperis_DSP_Failed_Logons.yaml) | Medium | InitialAccess, CredentialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [Semperis DSP Kerberos krbtgt account with old password](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/SemperisDSP_KerberoskrbtgtAccount.yaml) | Medium | CredentialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [Semperis DSP Mimikatz's DCShadow Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/SemperisDSP_EvidenceOfMimikatzDCShadowAttack.yaml) | High | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [Semperis DSP Operations Critical Notifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/Semperis_DSP_Operations_Critical_Notifications_.yaml) | Medium | InitialAccess, CredentialAccess, ResourceDevelopment | [`SecurityEvent`](../tables/securityevent.md) |
| [Semperis DSP RBAC Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/Semperis_DSP_RBAC_Changes.yaml) | Medium | PrivilegeEscalation, Persistence | [`SecurityEvent`](../tables/securityevent.md) |
| [Semperis DSP Recent sIDHistory changes on AD objects](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/SemperisDSP_RecentsIDHistoryChangesOnADObjects.yaml) | High | PrivilegeEscalation, Persistence | [`SecurityEvent`](../tables/securityevent.md) |
| [Semperis DSP Well-known privileged SIDs in sIDHistory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/SemperisDSP_WellKnownPrivilegedSIDsInsIDHistory.yaml) | Medium | PrivilegeEscalation, DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [Semperis DSP Zerologon vulnerability](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/SemperisDSP_ZerologonVulnerability.yaml) | Medium | PrivilegeEscalation | [`SecurityEvent`](../tables/securityevent.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SemperisDSPADChanges](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPADChanges.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [SemperisDSPNotifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPNotifications.json) | [`SecurityEvent`](../tables/securityevent.md) |
| [SemperisDSPQuickviewDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPQuickviewDashboard.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SecurityEvent`](../tables/securityevent.md) |
| [SemperisDSPSecurityIndicators](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPSecurityIndicators.json) | [`SecurityEvent`](../tables/securityevent.md) |
| [SemperisDSPWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPWorkbook.json) | [`SecurityEvent`](../tables/securityevent.md) |
| [workbooksMetadata](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/workbooksMetadata.json) | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [dsp_parser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Parsers/dsp_parser.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                             |
|-------------|--------------------------------|--------------------------------------------------------------------------------|
| 3.0.2       | 23-04-2025                     | Updated **Analytical Rule** and **Parser**   |
| 3.0.1       | 28-03-2025                     | Removed duplicate query and fixed query in **Workbook** SemperisDSPSecurityIndicators.   |
| 3.0.0       | 18-03-2025                     | Fixed correct function name in **Workbook** SemperisDSPSecurityIndicators.      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
