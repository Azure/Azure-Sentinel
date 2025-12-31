# ZeroTrust(TIC3.0)

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **20 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AuditLogs`](../tables/auditlogs.md) | Workbooks |
| [`AzureActivity`](../tables/azureactivity.md) | Workbooks |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Workbooks |
| [`CarbonBlack_Alerts_CL`](../tables/carbonblack-alerts-cl.md) | Workbooks |
| [`Crosswalk`](../tables/crosswalk.md) | Workbooks |
| [`DeviceRegistryEvents`](../tables/deviceregistryevents.md) | Workbooks |
| [`EmailAttachmentInfo`](../tables/emailattachmentinfo.md) | Workbooks |
| [`EmailEvents`](../tables/emailevents.md) | Workbooks |
| [`FakeData`](../tables/fakedata.md) | Workbooks |
| [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) | Workbooks |
| [`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md) | Workbooks |
| [`LogOns`](../tables/logons.md) | Workbooks |
| [`OfficeActivity`](../tables/officeactivity.md) | Workbooks |
| [`QualysHostDetectionV3_CL`](../tables/qualyshostdetectionv3-cl.md) | Workbooks |
| [`SecurityBaseline`](../tables/securitybaseline.md) | Workbooks |
| [`SecurityRecommendation`](../tables/securityrecommendation.md) | Analytics, Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | Workbooks |
| [`Usage`](../tables/usage.md) | Workbooks |
| [`VMConnection`](../tables/vmconnection.md) | Workbooks |

### Internal Tables

The following **4 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`BehaviorAnalytics`](../tables/behavioranalytics.md) | Workbooks |
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
| [ZeroTrust(TIC3.0) Control Assessment Posture Change](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Analytic%20Rules/Zero_Trust_TIC3.0_ControlAssessmentPostureChange.yaml) | Medium | Discovery | [`SecurityRecommendation`](../tables/securityrecommendation.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json) | [`AuditLogs`](../tables/auditlogs.md)<br>[`AzureActivity`](../tables/azureactivity.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`CarbonBlack_Alerts_CL`](../tables/carbonblack-alerts-cl.md)<br>[`Crosswalk`](../tables/crosswalk.md)<br>[`DeviceRegistryEvents`](../tables/deviceregistryevents.md)<br>[`EmailAttachmentInfo`](../tables/emailattachmentinfo.md)<br>[`EmailEvents`](../tables/emailevents.md)<br>[`FakeData`](../tables/fakedata.md)<br>[`GCP_IAM_CL`](../tables/gcp-iam-cl.md)<br>[`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md)<br>[`LogOns`](../tables/logons.md)<br>[`OfficeActivity`](../tables/officeactivity.md)<br>[`QualysHostDetectionV3_CL`](../tables/qualyshostdetectionv3-cl.md)<br>[`SecurityBaseline`](../tables/securitybaseline.md)<br>[`SecurityRecommendation`](../tables/securityrecommendation.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`Usage`](../tables/usage.md)<br>[`VMConnection`](../tables/vmconnection.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md)<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Create Jira Issue](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Playbooks/Open_JIRATicketRecommendation-ZeroTrust/Open_JIRATicketRecommendation-ZeroTrust.json) | This playbook will open a Jira Issue when a new incident is opened in Microsoft Sentinel. | - |
| [Create-AzureDevOpsTask](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Playbooks/Open_DevOpsTaskRecommendation-ZeroTrust/Open_DevOpsTaskRecommendation-ZeroTrust.json) | This playbook will create the Azure DevOps task filled with the Microsoft Sentinel incident details. | - |
| [Notify-GovernanceComplianceTeam](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Playbooks/Notify_GovernanceComplianceTeam-ZeroTrust/Notify_GovernanceComplianceTeam.json) | This Security Orchestration, Automation, & Response (SOAR) capability is designed for configuration ... | - |

## Additional Documentation

> 📄 *Source: [ZeroTrust(TIC3.0)/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust(TIC3.0)/README.md)*

# Overview
---
The Microsoft Sentinel Zero Trust (TIC 3.0) Solution provides a mechanism for viewing log queries aligned to Zero Trust and Trusted Internet Connections models across the Microsoft and partner ecosystem. This solution enables governance and compliance teams to design, build, monitor, and respond to Zero Trust (TIC 3.0) requirements across cloud, multi-cloud, 1st/3rd party workloads. The solution includes the new Zero Trust (TIC 3.0) Workbook, (1) Analytics Rule, and (3) Playbooks. While only Microsoft Sentinel and Microsoft Defender for Cloud are required to get started, the solution is enhanced with numerous Microsoft offerings. This Solution enables Security Architects, Engineers, SecOps Analysts, Managers, and IT Pros to gain situational awareness visibility for the security posture of cloud, multi-cloud, hybrid, and on-premise workloads. For more information, see 💡[Microsoft Zero Trust Model](https://www.microsoft.com/security/business/zero-trust) 💡[Trusted Internet Connections](https://www.cisa.gov/trusted-internet-connections)

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZeroTrust(TIC3.0)%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZeroTrust(TIC3.0)%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust(TIC3.0)/Workbooks/Images/ZeroTrust(TIC3.0)Black1.PNG?raw=true)

## Getting Started
This solution is designed to augment staffing through automation, machine learning, query/alerting generation, and visualizations. This workbook leverages Azure Policy, Azure Resource Graph, and Azure Log Analytics to align with Zero Trust (TIC 3.0) control requirements. A filter set is available for custom reporting by guides, subscriptions, workspaces, time-filtering, control family, and controls. This offering telemetry from 25+ Microsoft Security and partner offerings, while only Microsoft Sentinel and Microsoft Defender for Cloud are required to get started, each offering provides additional enrichment for aligning with control requirements. Each control includes a Control Card detailing an overview of requirements, primary/secondary controls, deep-links to referenced product pages/portals, recommendations, implementation guides, compliance cross-walks and tooling telemetry for building situational awareness of cloud workloads. 


*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                            |
|-------------|--------------------------------|-----------------------------------------------------------------------------------------------|
| 3.0.2       | 11-09-2025                     | Removed the network map from the workbook.                      |
| 3.0.1       | 31-01-2024                     | Updated the solution to fix Analytic Rules deployment issue     |
| 3.0.0       | 09-11-2023                     |	Changes for rebranding from Azure Active Directory Identity Protection to Microsoft Entra ID Protection |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
