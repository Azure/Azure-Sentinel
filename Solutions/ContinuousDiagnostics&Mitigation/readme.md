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

### [Microsoft Sentinel Roles](https://docs.microsoft.com/azure/sentinel/roles) / [Microsoft Defender for Cloud Roles](https://docs.microsoft.com/azure/defender-for-cloud/permissions#roles-and-allowed-actions) / [Microsoft Defender for Endpoint Roles](https://docs.microsoft.com/microsoft-365/security/defender-endpoint/user-roles)
| <strong> Roles </strong> | <strong> Rights </strong> | 
|:--|:--|
|Security Reader | View Workbooks, Analytics, Hunting, Security Recommendations |
|Security Contributor| Deploy/Modify Workbooks, Analytics, Hunting Queries, Apply Security Recommendations |
|Security Admin| Onboard & Configure Endpoints |
|Owner| Assign Regulatory Compliance Initiatives|

### Onboarding Prerequisites 
1️⃣ [Onboard Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard)<br>
2️⃣ [Onboard Microsoft Defender for Cloud](https://docs.microsoft.com/azure/security-center/security-center-get-started)<br>
3️⃣ [Onboard Microsoft Defender for Endpoint](https://docs.microsoft.com/microsoft-365/security/defender-endpoint/onboard-configure)<br>
4️⃣ [Enable Microsoft Defender for Endpoint: Threat & Vulnerability Management](https://docs.microsoft.com/microsoft-365/security/defender-endpoint/tvm-prerequisites)<br>
5️⃣ [Connect Microsoft Defender for Cloud to Microsoft Sentinel via Continuous Export](https://docs.microsoft.com/azure/security-center/continuous-export)<br>
6️⃣ [Extend Microsoft Sentinel Across Workspaces and Tenants](https://docs.microsoft.com/azure/sentinel/extend-sentinel-across-workspaces-tenants)<br>
7️⃣ [Connect Microsoft Defender for Endpoint to Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/connect-microsoft-365-defender?tabs=MDE)<br>
8️⃣ [Automated Data Export to CISA](https://docs.microsoft.com/azure/sentinel/connect-microsoft-365-defender?tabs=MDE)<br>
9️⃣ [Add the Microsoft Defender for Cloud: NIST SP 800-53 R4 & R5 Assessments to Your Dashboard](https://docs.microsoft.com/azure/security-center/update-regulatory-compliance-packages#add-a-regulatory-standard-to-your-dashboard)<br>


## Print/Export Report
1️⃣ Set Background Theme: Settings > Appearance > Theme: Azure > Apply<br>
2️⃣ Print/Export Report: More Content Actions (...) > Print Content<br>
3️⃣ Settings: Layout (Landscape), Pages (All), Print (One Sided), Scale (60), Pages Per Sheet (1), Quality (1,200 DPI), Margins (None) > Print<br>

## Workbook
The Microsoft Sentinel: Continuous Diagnostics & Mitigation (CDM) workbook provides a dashboard for viewing log queries, azure resource graph, metrics, and policies aligned to requirements in the CDM program which is cross-walked across the Microsoft portfolio including Azure, Microsoft 365, Multi-Cloud, Hybrid, and On-Premises workloads. This workbook enables Security Architects, Engineers, SecOps Analysts, Managers, and IT Pros to gain situational awareness visibility for the security posture of cloud workloads. There are also recommendations for selecting, designing, deploying, and configuring Microsoft offerings for alignment with respective CDM program requirements and practices.

## Hunting Queries
### CDM_ContinuousDiagnostics&Mitigation_Posture
This hunting query is designed to monitor Azure policies aligned with the Continuous Diagnostics & Mitigation (CDM) Program. It provides a policy check assessment of current CDM policy status across capability areas.<br>

## Analytics
### CDM_ContinuousDiagnostics&Mitigation_PostureChanged
This alert is designed to monitor Azure policies aligned with the Continuous Diagnostics & Mitigation (CDM) Program. The alert triggers when policy compliance falls below 70% within a 1 week time-frame.<br>

## Disclaimer
The Microsoft Sentinel CDM Solution is not endorsed, nor required by the CDM PMO or CISA. The offering is also not a replacement for the CDM program's requirement for agency dashboard integration. While the offering does have similar visibility metrics, the agency and service integrator are still responsible for ensuring relevant cloud and asset data are integrated into the agency dashboard in accordance with CDM Program requirements. Similar, while Microsoft Sentinel CDM may make data aggregation and availability more rapid and efficient, the offering should not be viewed as a replacement for any specific CDM capability, until independently validated by appropriate CISA CDM contractor or federal teams. 