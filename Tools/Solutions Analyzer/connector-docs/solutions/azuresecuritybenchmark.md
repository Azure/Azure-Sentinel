# AzureSecurityBenchmark

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **15 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AADUserRiskEvents`](../tables/aaduserriskevents.md) | Workbooks |
| [`AuditLogs`](../tables/auditlogs.md) | Workbooks |
| [`AzureActivity`](../tables/azureactivity.md) | Workbooks |
| [`AzureDevOpsAuditing`](../tables/azuredevopsauditing.md) | Workbooks |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Workbooks |
| [`Crosswalk`](../tables/crosswalk.md) | Workbooks |
| [`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md) | Workbooks |
| [`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md) | Workbooks |
| [`LogOns`](../tables/logons.md) | Workbooks |
| [`ProtectionStatus`](../tables/protectionstatus.md) | Workbooks |
| [`SecurityNestedRecommendation`](../tables/securitynestedrecommendation.md) | Workbooks |
| [`SecurityRecommendation`](../tables/securityrecommendation.md) | Analytics |
| [`SecurityRegulatoryCompliance`](../tables/securityregulatorycompliance.md) | Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | Workbooks |
| [`securityresources`](../tables/securityresources.md) | Workbooks |

### Internal Tables

The following **3 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`BehaviorAnalytics`](../tables/behavioranalytics.md) | Workbooks |
| [`SecurityAlert`](../tables/securityalert.md) | Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | Workbooks |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 3 |
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Azure Security Benchmark Posture Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Analytic%20Rules/AzureSecurityBenchmarkPostureChanged.yaml) | Medium | Discovery | [`SecurityRecommendation`](../tables/securityrecommendation.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AzureSecurityBenchmark](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/AzureSecurityBenchmark.json) | [`AADUserRiskEvents`](../tables/aaduserriskevents.md)<br>[`AuditLogs`](../tables/auditlogs.md)<br>[`AzureActivity`](../tables/azureactivity.md)<br>[`AzureDevOpsAuditing`](../tables/azuredevopsauditing.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`Crosswalk`](../tables/crosswalk.md)<br>[`GitHubAuditLogPolling_CL`](../tables/githubauditlogpolling-cl.md)<br>[`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md)<br>[`LogOns`](../tables/logons.md)<br>[`ProtectionStatus`](../tables/protectionstatus.md)<br>[`SecurityNestedRecommendation`](../tables/securitynestedrecommendation.md)<br>[`SecurityRegulatoryCompliance`](../tables/securityregulatorycompliance.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>[`securityresources`](../tables/securityresources.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Create Jira Issue](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Playbooks/Open_JIRATicketRecommendation-ASB/Open_JIRATicketRecommendation-ASB.json) | This playbook will open a Jira Issue when a new incident is opened in Microsoft Sentinel. | - |
| [Create-AzureDevOpsTask](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Playbooks/Open_DevOpsTaskRecommendation-ASB/Open_DevOpsTaskRecommendation-ASB.json) | This playbook will create the Azure DevOps task filled with the Microsoft Sentinel incident details. | - |
| [Notify-GovernanceComplianceTeam](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Playbooks/Notify_GovernanceComplianceTeam-SecurityBenchmark/Notify_GovernanceComplianceTeam.json) | This Security Orchestration, Automation, & Response (SOAR) capability is designed for configuration ... | - |

## Additional Documentation

> 📄 *Source: [AzureSecurityBenchmark/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/README.md)*

# Overview
---
## Microsoft Sentinel: Azure Security Benchmark Solution
The Azure Security Benchmark v3 Solution is designed to enable Cloud Architects, Security Engineers, and Governance Risk Compliance Professionals to gain situational awareness for cloud security posture and hardening. Benchmark recommendations provide a starting point for selecting specific security configuration settings and facilitate risk reduction. The Azure Security Benchmark includes a collection of high-impact security recommendations for improving posture. This workbook provides visibility and situational awareness for security capabilities delivered with Microsoft technologies in predominantly cloud-based environments. Customer experience will vary by user and some panels may require additional configurations for operation.

## Try on Portal
You can deploy the workbook by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAzureSecurityBenchmark%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAzureSecurityBenchmark%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/Images/AzureSecurityBenchmark1.png?raw=true)<br>
![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/Images/AzureSecurityBenchmark2.png?raw=true)<br>
![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/Images/AzureSecurityBenchmark3.png?raw=true)<br>

## Getting Started

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                         |
|-------------|--------------------------------|----------------------------------------------------------------------------|
| 3.0.3       | 10-09-2025                     | Removed the network map from the workbook.                      |
| 3.0.2       | 12-04-2024                     | Updated Entity Mappings                                         |
| 3.0.1       | 24-01-2023                     | Updated the solution to fix **Analytic Rules** deployment issue |
| 3.0.0       | 28-11-2023                     | Changes for rebranding from Azure Active Directory to Microsoft Entra ID & MS 365 Defender to MS Defender XDR |
| 3.0.0       | 28-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID & MS 365 Defender to MS Defender XDR |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
