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
|Owner| Assign Regulatory Compliance Initiatives|

### Onboarding Prerequisites 
1️⃣ [Access Microsoft 365 Compliance Manager: Assessments](https://compliance.microsoft.com/compliancemanager?viewid=Assessments)<br>
2️⃣ [Onboard Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard)<br>
3️⃣ [Onboard Microsoft Defender for Cloud](https://docs.microsoft.com/azure/security-center/security-center-get-started)<br>
4️⃣ [Add the Microsoft Defender for Cloud: NIST SP 800-53 R4 & R5 Assessments to Your Dashboard](https://docs.microsoft.com/azure/security-center/update-regulatory-compliance-packages#add-a-regulatory-standard-to-your-dashboard)<br>
5️⃣ [Continuously Export Security Center Data to Log Analytics Workspace](https://docs.microsoft.com/azure/security-center/continuous-export)<br>
6️⃣ [Extend Microsoft Sentinel Across Workspaces and Tenants](https://docs.microsoft.com/azure/sentinel/extend-sentinel-across-workspaces-tenants)<br>
7️⃣ [Configure Auto Provisioning of Microsoft Defender for Cloud Agents](https://docs.microsoft.com/azure/defender-for-cloud/enable-data-collection)<br>
8️⃣ [Review Microsoft Service Trust Portal Documentation/Audit/Resources](https://servicetrust.microsoft.com/)<br>

## Workbook
### 1) NIST SP 800-53 Workbook
The Microsoft Sentinel: NIST SP 800-53 Workbook provides a dashboard for viewing log queries, azure resource graph, metrics, and policies aligned to requirements across the Microsoft portfolio including Azure, Microsoft 365, Multi-Cloud, Hybrid, and On-Premises workloads. This workbook enables Security Architects, Engineers, SecOps Analysts, Managers, and IT Pros to gain situational awareness visibility for the security posture of cloud workloads. There are also recommendations for selecting, designing, deploying, and configuring Microsoft offerings for alignment with respective requirements.<br>

## Analytics
### 1) NIST SP 800-53 Posture Changed
This alert is designed to monitor Azure policies aligned with the NIST SP 800-53 Regulatory Compliance Initiative. The alert triggers when policy compliance falls below 70% within a 1 week time-frame. For more information, see 💡[Details of the NIST SP 800-53 Rev. 4 Regulatory Compliance built-in initiative](https://docs.microsoft.com/azure/governance/policy/samples/nist-sp-800-53-)<br>

## Playbooks
### 1) Notify-GovernanceComplianceTeam
This Security Orchestration, Automation, & Response (SOAR) capability is designed for configuration with the solution's analytics rules. When analytics rules trigger this automation notifies the governance compliance team of respective details via Teams chat and exchange email. This automation reduces requirements to manually monitor the workbook or analytics rules while increasing response times.<br>
### 2) Create-AzureDevOpsTask
This Security Orchestration, Automation, & Response (SOAR) capability is designed to create an Azure DevOps Task when a Microsoft Defender for Cloud recommendation is triggered. This automation enables a consistent response when resources become unhealthy relative to a predefined recommendation, enabling teams to focus on remediation and improving response times.
### 3) Open-jira-Ticket
This Security Orchestration, Automation, & Response (SOAR) capability is designed to open a Jira issue when an recommendation is unhealthy in Microsoft Defender for Cloud. This automation improves time to response by providing consistent notifications when resources become unhealthy relative to a predefined recommendation.

### Print/Export Reports
1️⃣ Set Background Theme: Settings > Appearance > Theme: Azure > Apply<br>
2️⃣ Print/Export Report: More Content Actions (...) > Print Content<br>
3️⃣ Settings: Layout (Landscape), Pages (All), Print (One Sided), Scale (60), Pages Per Sheet (1), Quality (1,200 DPI), Margins (None) > Print<br>
4️⃣ Executive Summary: Microsoft Defender for Cloud > Regulatory Compliance > Download Report > Report Standard (NIST SP 800 53 R4), Format (PDF)

### Important
Each control below is associated with one or more 💡[Azure Policy](https://docs.microsoft.com/azure/governance/policy/overview) definitions. These policies may help you 💡[Assess Compliance](https://docs.microsoft.com/azure/governance/policy/how-to/get-compliance-data) with the control; however, there often is not a one-to-one or complete match between a control and one or more policies. As such, Compliant in Azure Policy refers only to the policy definitions themselves; this doesn't ensure you're fully compliant with all requirements of a control. In addition, the compliance standard includes controls that aren't addressed by any Azure Policy definitions at this time. Therefore, compliance in Azure Policy is only a partial view of your overall compliance status. The associations between compliance domains, controls, and Azure Policy definitions for this compliance standard may change over time. To view the change history, see the 💡[GitHub Commit History](https://github.com/Azure/azure-policy/commits/master/built-in-policies/policySetDefinitions/Regulatory%20Compliance/NIST80053_audit.json). For more information, see 💡[Details of the NIST SP 800-53 Regulatory Compliance built-in initiative](https://docs.microsoft.com/azure/governance/policy/samples/nist-sp-800-53-r4)

Customer experience will vary by user and some panels may require additional configurations for operation. Recommendations do not imply coverage of respective controls as they are often one of several courses of action for approaching requirements which is unique to each customer. Recommendations should be considered a starting point for planning full or partial coverage of respective requirements. This workbook does not address all controls within the framework. It should be considered a supplemental tool to gain visibility of technical controls within cloud, multi-cloud, and hybrid networks. For the full listing of respective controls, see the💡[Microsoft Cloud Service Trust Portal](https://servicetrust.microsoft.com/)
