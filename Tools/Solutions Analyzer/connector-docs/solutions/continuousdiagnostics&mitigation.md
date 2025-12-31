# ContinuousDiagnostics&Mitigation

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-08-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **18 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AlertsWithTiObservables`](../tables/alertswithtiobservables.md) | Workbooks |
| [`AuditLogs`](../tables/auditlogs.md) | Workbooks |
| [`AzureDevOpsAuditing`](../tables/azuredevopsauditing.md) | Workbooks |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Workbooks |
| [`ConfigurationData`](../tables/configurationdata.md) | Workbooks |
| [`Crosswalk`](../tables/crosswalk.md) | Workbooks |
| [`DeviceEvents`](../tables/deviceevents.md) | Workbooks |
| [`DeviceFileEvents`](../tables/devicefileevents.md) | Workbooks |
| [`DeviceLogonEvents`](../tables/devicelogonevents.md) | Workbooks |
| [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md) | Workbooks |
| [`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md) | Workbooks |
| [`SecurityEvent`](../tables/securityevent.md) | Workbooks |
| [`SecurityNestedRecommendation`](../tables/securitynestedrecommendation.md) | Workbooks |
| [`SecurityRecommendation`](../tables/securityrecommendation.md) | Analytics, Hunting, Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | Workbooks |
| [`managedservicesresources`](../tables/managedservicesresources.md) | Workbooks |
| [`securityresources`](../tables/securityresources.md) | Workbooks |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Hunting Queries | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [CDM_ContinuousDiagnostics&Mitigation_PostureChanged](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Analytic%20Rules/ContinuousDiagnostics%26MitigationPostureChanged.yaml) | Medium | Discovery | [`SecurityRecommendation`](../tables/securityrecommendation.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [CDM_ContinuousDiagnostics&Mitigation_Posture](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Hunting%20Queries/ContinuousDiagnostics%26MitigationPosture.yaml) | Discovery | [`SecurityRecommendation`](../tables/securityrecommendation.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ContinuousDiagnostics&Mitigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Workbooks/ContinuousDiagnostics%26Mitigation.json) | [`AlertsWithTiObservables`](../tables/alertswithtiobservables.md)<br>[`AuditLogs`](../tables/auditlogs.md)<br>[`AzureDevOpsAuditing`](../tables/azuredevopsauditing.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`ConfigurationData`](../tables/configurationdata.md)<br>[`Crosswalk`](../tables/crosswalk.md)<br>[`DeviceEvents`](../tables/deviceevents.md)<br>[`DeviceFileEvents`](../tables/devicefileevents.md)<br>[`DeviceLogonEvents`](../tables/devicelogonevents.md)<br>[`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityNestedRecommendation`](../tables/securitynestedrecommendation.md)<br>[`SecurityRecommendation`](../tables/securityrecommendation.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`managedservicesresources`](../tables/managedservicesresources.md)<br>[`securityresources`](../tables/securityresources.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

## Additional Documentation

> 📄 *Source: [ContinuousDiagnostics&Mitigation/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics&Mitigation/README.md)*

# Overview
---
## Microsoft Sentinel: Continuous Diagnostics & Mitigation (CDM) Solution
This Solution enables Compliance Teams, Architects, SecOps Analysts, and Consultants to gain situational awareness for cloud workload security posture. This solution is designed to augment staffing through automation, visibility, assessment, monitoring and remediation. This solution includes (1) Workbook for build/design/reporting, (1) Analytics rule for monitoring and (1) Hunting query for assessment. "The Cybersecurity and Infrastructure Security Agency (CISA) Continuous Diagnostics and Mitigation (CDM) Program is a dynamic approach to fortifying the cybersecurity of government networks and systems. The CDM Program provides cybersecurity tools, integration services, and dashboards to participating agencies to help them improve their respective security postures by delivering better visibility and awareness of their 
networks and defending against cyber adversaries." For more information, see 💡[Continuous Diagnostics and Mitigation (CDM)](https://www.cisa.gov/cdm).

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FContinuousDiagnostics&Mitigation%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FContinuousDiagnostics&Mitigation%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics&Mitigation/Workbooks/Images/ContinuousDiagnostics&MitigationBlack.png?raw=true)

## Getting Started
This Solution enables Compliance Teams, Architects, SecOps Analysts, and Consultants to gain situational awareness for cloud workload security posture. This solution is designed to augment staffing through automation, visibility, assessment, monitoring and remediation. This Solution demonstrates best practice guidance, but Microsoft does not guarantee nor imply compliance. All CDM requirements, validations, and controls are governed by the 💡[Cybersecurity & Infrastructure Security Agency](https://www.cisa.gov/cdm). This solution provides visibility and situational awareness for security capabilities delivered with Microsoft technologies in predominantly cloud-based environments. Customer experience will vary by user and some panels may require additional configurations for operation. Recommendations do not imply coverage of respective controls as they are often one of several courses of action for approaching requirements which is unique to each customer.<br>


*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                            |
|-------------|--------------------------------|-----------------------------------------------------------------------------------------------|
| 3.0.2       | 29-09-2025                     |	Updated the broken metrics in the workbook                  |
| 3.0.1       | 29-01-2024                     |	Updated the solution to fix Analytic Rules deployment issue |
| 3.0.0       | 09-11-2023                     |	Changes for rebranding from Azure Active Directory Identity Protection to Microsoft Entra ID Protection |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
