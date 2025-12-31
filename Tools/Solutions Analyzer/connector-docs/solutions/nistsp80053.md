# NISTSP80053

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-02-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **22 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AADUserRiskEvents`](../tables/aaduserriskevents.md) | Workbooks |
| [`AWSCloudTrail`](../tables/awscloudtrail.md) | Workbooks |
| [`AuditLogs`](../tables/auditlogs.md) | Workbooks |
| [`AzureActivity`](../tables/azureactivity.md) | Workbooks |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Workbooks |
| [`CarbonBlack_Alerts_CL`](../tables/carbonblack-alerts-cl.md) | Workbooks |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Workbooks |
| [`ConfigurationChange`](../tables/configurationchange.md) | Workbooks |
| [`Crosswalk`](../tables/crosswalk.md) | Workbooks |
| [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) | Workbooks |
| [`InformationProtectionEvents`](../tables/informationprotectionevents.md) | Workbooks |
| [`OfficeActivity`](../tables/officeactivity.md) | Workbooks |
| [`QualysHostDetectionV3_CL`](../tables/qualyshostdetectionv3-cl.md) | Workbooks |
| [`SecureScores`](../tables/securescores.md) | Workbooks |
| [`SecurityBaseline`](../tables/securitybaseline.md) | Workbooks |
| [`SecurityEvent`](../tables/securityevent.md) | Workbooks |
| [`SecurityRecommendation`](../tables/securityrecommendation.md) | Analytics, Workbooks |
| [`SecurityRegulatoryCompliance`](../tables/securityregulatorycompliance.md) | Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | Workbooks |
| [`Usage`](../tables/usage.md) | Workbooks |
| [`securityresources`](../tables/securityresources.md) | Workbooks |

### Internal Tables

The following **3 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`IdentityInfo`](../tables/identityinfo.md) | Workbooks |
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
| [NIST SP 800-53 Posture Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Analytic%20Rules/NISTSP80053PostureChanged.yaml) | Medium | Discovery | [`SecurityRecommendation`](../tables/securityrecommendation.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json) | [`AADUserRiskEvents`](../tables/aaduserriskevents.md)<br>[`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`AuditLogs`](../tables/auditlogs.md)<br>[`AzureActivity`](../tables/azureactivity.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`CarbonBlack_Alerts_CL`](../tables/carbonblack-alerts-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ConfigurationChange`](../tables/configurationchange.md)<br>[`Crosswalk`](../tables/crosswalk.md)<br>[`GCP_IAM_CL`](../tables/gcp-iam-cl.md)<br>[`InformationProtectionEvents`](../tables/informationprotectionevents.md)<br>[`OfficeActivity`](../tables/officeactivity.md)<br>[`QualysHostDetectionV3_CL`](../tables/qualyshostdetectionv3-cl.md)<br>[`SecureScores`](../tables/securescores.md)<br>[`SecurityBaseline`](../tables/securitybaseline.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityRecommendation`](../tables/securityrecommendation.md)<br>[`SecurityRegulatoryCompliance`](../tables/securityregulatorycompliance.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`Usage`](../tables/usage.md)<br>[`securityresources`](../tables/securityresources.md)<br>*Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md)<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Create Jira Issue](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Playbooks/CreateJiraIssue/Open_JIRATicketRecommendation.json) | This playbook will open a Jira Issue when a new incident is opened in Microsoft Sentinel. | - |
| [Create-AzureDevOpsTask](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Playbooks/Create-AzureDevOpsTask/Open_DevOpsTaskRecommendation.json) | This playbook will create the Azure DevOps task filled with the Microsoft Sentinel incident details. | - |
| [Notify_GovernanceComplianceTeam](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Playbooks/Notify_GovernanceComplianceTeam/Notify_GovernanceComplianceTeam.json) | This playbook will create the Azure DevOps task filled with the Microsoft Sentinel incident details. | - |

## Additional Documentation

> 📄 *Source: [NISTSP80053/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/README.md)*

# Overview
---
## Microsoft Sentinel: NIST SP 800-53 Solution
This Solution enables Compliance Teams, Architects, SecOps Analysts, and Consultants to gain situational awareness for cloud workload security posture. This Solution is designed to augment staffing through automation, visibility, assessment, monitoring and remediation. The Microsoft Sentinel: NIST SP 800-53 Solution demonstrates best practice guidance, but Microsoft does not guarantee nor imply compliance. All requirements, validations, and controls are governed by the 💡[National Institute of Standards and Technology (NIST)](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FNISTSP80053%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FNISTSP80053%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/Images/NISTSP80053Black.png?raw=true)

## Getting Started
This solution is designed to augment staffing through automation, machine learning, query/alerting generation, and visualizations. This workbook leverages Azure Policy, Azure Resource Graph, and Azure Log Analytics to align with NIST SP 800-53 control requirements. A filter set is available for custom reporting by guides, subscriptions, workspaces, time-filtering, control family, and controls. This offering telemetry from 25+ Microsoft Security products (1P/3P/Multi-Cloud/Hybrid/On-Premises), while only Microsoft Sentinel/Microsoft Defender for Cloud are required to get started, each offering provides additional enrichment for aligning with control requirements. Each NIST SP 800-53 control includes a Control Card detailing an overview of requirements, primary/secondary controls, deep-links to referenced product pages/portals, recommendations, implementation guides, compliance cross-walks and tooling telemetry for building situational awareness of cloud workloads.

### [Recommended Microsoft Sentinel Roles](https://docs.microsoft.com/azure/sentinel/roles) / [Recommended Microsoft Defender for Cloud Roles](https://docs.microsoft.com/azure/defender-for-cloud/permissions#roles-and-allowed-actions)
| <strong> Roles </strong> | <strong> Rights </strong> | 
|:--|:--|
|Security Reader | View Workbooks, Analytics, Hunting, Security Recommendations |
|Security Contributor| Deploy/Modify Workbooks, Analytics, Hunting Queries, Apply Security Recommendations |
|Automation Contributor| Deploy/Modify Playbooks & Automation Rules |

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                            |
|-------------|--------------------------------|-----------------------------------------------------------------------------------------------|
| 3.0.2       | 23-09-2025                     | Updated the workbook with new links and fixed broken metrics.   |
| 3.0.1       | 31-01-2024                     | Updated the solution to fix Analytic Rules deployment issue     |
| 3.0.0       | 09-11-2023                     |	Changes for rebranding from Azure Active Directory Identity Protection to Microsoft Entra ID Protection |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
