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

### [Recommended Microsoft Sentinel Roles](https://docs.microsoft.com/azure/sentinel/roles) / [Recommended Microsoft Defender for Cloud Roles](https://docs.microsoft.com/azure/defender-for-cloud/permissions#roles-and-allowed-actions)
| <strong> Roles </strong> | <strong> Rights </strong> | 
|:--|:--|
|Security Reader | View Workbooks, Analytics, Hunting, Security Recommendations |
|Security Contributor| Deploy/Modify Workbooks, Analytics, Hunting Queries, Apply Security Recommendations |
|Automation Contributor| Deploy/Modify Playbooks & Automation Rules |

### Onboarding Prerequisites 
1️⃣ [Access Microsoft 365 Compliance Manager: Assessments](https://compliance.microsoft.com/compliancemanager?viewid=Assessments)<br>
2️⃣  [Onboard Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard)<br>
3️⃣  [Onboard Microsoft Defender for Cloud](https://docs.microsoft.com/azure/security-center/security-center-get-started)<br>
4️⃣ [Continuously Export Security Center Data to Log Analytics Workspace](https://docs.microsoft.com/azure/security-center/continuous-export)<br>
5️⃣ [Extend Microsoft Sentinel Across Workspaces and Tenants](https://docs.microsoft.com/azure/sentinel/extend-sentinel-across-workspaces-tenants)<br>
6️⃣ [Configure Auto Provisioning of Microsoft Defender for Cloud Agents](https://docs.microsoft.com/azure/defender-for-cloud/enable-data-collection)<br>
7️⃣ [Review Microsoft Service Trust Portal Documentation/Audit/Resources](https://servicetrust.microsoft.com/)<br>

### Recommended Enrichments
✳️[Microsoft Entra ID](https://azure.microsoft.com/services/active-directory/)<br>
✳️[Microsoft Defender for Office 365](https://www.microsoft.com/microsoft-365/security/office-365-defender)<br>
✳️[Azure Firewall Premium](https://azure.microsoft.com/services/azure-firewall)<br>
✳️[Microsoft Defender for Endpoint](https://www.microsoft.com/microsoft-365/security/endpoint-defender)<br>
✳️[Azure Virtual Desktop](https://azure.microsoft.com/services/virtual-desktop/)<br>
✳️[Azure Web Application Firewall](https://azure.microsoft.com/services/web-application-firewall/)<br>
✳️[Azure Information Protection](https://azure.microsoft.com/services/information-protection/)<br>
✳️[Microsoft 365 Defender](https://www.microsoft.com/microsoft-365/security/microsoft-365-defender)<br>
✳️[Microsoft Defender for Cloud Apps](https://www.microsoft.com/microsoft-365/enterprise-mobility-security/cloud-app-security)<br>
✳️[Key Vault](https://azure.microsoft.com/services/key-vault/)<br>
✳️[Azure DDoS Protection](https://azure.microsoft.com/services/ddos-protection/)<br>
✳️[Microsoft Defender for Identity](https://www.microsoft.com/microsoft-365/security/identity-defender)<br>

### Print/Export Report
1️⃣ Set Background Theme: Settings > Appearance > Theme: Azure > Apply<br>
2️⃣ Print/Export Report: More Content Actions (...) > Print Content<br>
3️⃣ Settings: Layout (Landscape), Pages (All), Print (One Sided), Scale (60), Pages Per Sheet (1), Quality (1,200 DPI), Margins (None) > Print<br>

### Workbooks
The Microsoft Sentinel Zero Trust (TIC 3.0) Workbook provides a mechanism for viewing log queries aligned to Zero Trust and Trusted Internet Connections models across the Microsoft portfolio including Microsoft security offerings, Office 365 and many more. This workbook enables Security Architects, Engineers, SecOps Analysts, Managers, and IT Pros to gain situational awareness visibility for the security posture of cloud workloads. There are also recommendations for selecting, designing, deploying, and configuring Microsoft offerings for alignment with respective security best practice. 

### Analytics Rule
The Microsoft Sentinel Zero Trust (TIC 3.0) Analytic rule leverages Microsoft Defender for Cloud Security Recommendations to measure Zero Trust posture alignment across (11) TIC 3.0 control families. The default configuration is set for scheduled rules running every 7 days to reduce alert overload. The default configuration is to alert when posture compliance is below 70% and this number is configurable per organizational requirements. 

### Playbooks
### 1) Notify Governance Compliance Team
This Security Orchestration, Automation, & Response (SOAR) capability is designed for configuration with the solution's analytics rules. When analytics rules trigger this automation notifies the governance compliance team of respective details via Teams chat and exchange email. This automation reduces requirements to manually monitor the workbook or analytics rules while increasing response times.<br>
### 2) Open DevOps Task based on Recommendation
This Security Orchestration, Automation, & Response (SOAR) capability is designed to create an Azure DevOps Task when a Microsoft Defender for Cloud recommendation is triggered. This automation enables a consistent response when resources become unhealthy relative to a predefined recommendation, enabling teams to focus on remediation and improving response times.
### 3) Open JIRA Ticket based on Recommendation
This Security Orchestration, Automation, & Response (SOAR) capability is designed to open a Jira issue when an recommendation is unhealthy in Microsoft Defender for Cloud. This automation improves time to response by providing consistent notifications when resources become unhealthy relative to a predefined recommendation.

### Disclaimer
The Microsoft Sentinel Zero Trust (TIC 3.0) Solution demonstrates best practice guidance, but Microsoft does not guarantee nor imply compliance. All TIC requirements, validations, and controls are governed by the 💡 [Cybersecurity & Infrastructure Security Agency](https://www.cisa.gov/trusted-internet-connections). This workbook provides visibility and situational awareness for control requirements delivered with Microsoft technologies in predominantly cloud-based environments. Customer experience will vary by user and some panels may require additional configurations and query modification for operation. Recommendations do not imply coverage of respective controls as they are often one of several courses of action for approaching requirements which is unique to each customer. Recommendations should be considered a starting point for planning full or partial coverage of respective control requirements.

### Important
This solution provides visibility and situational awareness for security capabilities delivered with Microsoft technologies in predominantly cloud-based environments. Customer experience will vary by user and some panels may require additional configurations for operation. Recommendations do not imply coverage of respective controls as they are often one of several courses of action for approaching requirements which is unique to each customer. Recommendations should be considered a starting point for planning full or partial coverage of respective requirements. Each control is associated with one or more 💡[Azure Policy](https://docs.microsoft.com/azure/governance/policy/overview) definitions. These policies may help you 💡[assess compliance](https://docs.microsoft.com/azure/governance/policy/how-to/get-compliance-data) with the control; however, there often is not a one-to-one or complete match between a control and one or more policies. As such, Compliant in Azure Policy refers only to the policy definitions themselves; this doesn't ensure you're fully compliant with all requirements of a control. In addition, the compliance standard includes controls that aren't addressed by any Azure Policy definitions at this time. Therefore, compliance in Azure Policy is only a partial view of your overall compliance status. The associations between compliance domains, controls, and Azure Policy definitions for this compliance standard may change over time. 