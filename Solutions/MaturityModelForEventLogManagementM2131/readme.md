# Overview
---
## Microsoft Sentinel: Maturity Model for Event Log Management (M-21-31) Solution
This solution is designed to enable Cloud Architects, Security Engineers, and Governance Risk Compliance Professionals to increase visibility before, during, and after a cybersecurity incident. The solution includes (1) workbook, (4) hunting queries, (8) analytics rules, and (3) playbooks providing a comprehensive approach to design, build, monitoring, and response in logging architectures. Information from logs on information systems1 (for both on-premises systems and connections hosted by third parties, such as cloud services providers (CSPs) is invaluable in the detection, investigation, and remediation of cyber threats. "Executive Order 14028, Improving the Nation's Cybersecurity, directs decisive action to improve the Federal Government’s investigative and remediation capabilities. This memorandum was developed in accordance with and addresses the requirements in section 8 of the Executive Order for logging, log retention, and log management, with a focus on ensuring centralized access and visibility for the highest-level enterprise security operations center (SOC) of each agency. In addition, this memorandum establishes requirements for agencies3 to increase the sharing of such information, as needed and appropriate, to accelerate incident response efforts and to enable more effective defense of Federal information and executive branch departments and agencies." For more information, see 💡[Improving the Federal Government’s Investigative and Remediation Capabilities Related to Cybersecurity Incidents (M-21-31)](https://www.whitehouse.gov/wp-content/uploads/2021/08/M-21-31-Improving-the-Federal-Governments-Investigative-and-Remediation-Capabilities-Related-to-Cybersecurity-Incidents.pdf).

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMaturityModelForEventLogManagementM2131%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMaturityModelForEventLogManagementM2131%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/Images/MaturityModelForEventLogManagement_M2131Black.png?raw=true)

## Getting Started
The Microsoft Sentinel: Maturity Model for Event Log Management (M-21-31) Solution leverages Azure Policy, Azure Resource Graph, and Azure Log Analytics to align directly with the requirements outlined in the Executive Office of the President: Office of Management & Budget Memorandum (M-21-31): Improving the Federal Government's Investigative and Remediation Capabilities Related to Cybersecurity Incidents. This solution provides the capability to design, build, monitor, and remediate event log management. The Solution includes (1) Workbook for reporting, (8) Analytics Rules for monitoring, (4) Hunting Queries for assessment, and (3) Playbooks for response/remediation. The documentation below provides getting started recommendations for centralizing log analytics data and enabling Microsoft Defender for Cloud Continuous Export. This offering includes telemetry from 25+ Microsoft and Third Party products. Common use cases include conducting M-21-31 assessments via custom reporting, time filtering, subscription filtering, workspace filtering, and guides. The report is exportable for print or PDF with the Print Workbook feature. The workbook is organized by Event Logging Tiers (1-3) which highlight maturity from basic to advanced levels. There are multiple requirements within each Event Logging Tier, each covered by a Control Card. Control Cards include requirements summary, reference documentation links, recommendations for build/design, technology mapping, telemetry over time, and product/portal pages.<br> For more information, see 💡[Improving the Federal Government’s Investigative and Remediation Capabilities Related to Cybersecurity Incidents (M-21-31)](https://www.whitehouse.gov/wp-content/uploads/2021/08/M-21-31-Improving-the-Federal-Governments-Investigative-and-Remediation-Capabilities-Related-to-Cybersecurity-Incidents.pdf)<br>

## [Recommended Microsoft Sentinel Roles](https://docs.microsoft.com/azure/sentinel/roles) / [Recommended Microsoft Defender for Cloud Roles](https://docs.microsoft.com/azure/defender-for-cloud/permissions#roles-and-allowed-actions)
| <strong> Roles </strong> | <strong> Rights </strong> | 
|:--|:--|
|Security Reader | View Workbooks, Analytics, Hunting, Security Recommendations |
|Security Contributor| Deploy/Modify Workbooks, Analytics, Hunting Queries, Apply Security Recommendations |
|Automation Contributor| Deploy/Modify Playbooks & Automation Rules |
|Owner| Assign Regulatory Compliance Initiatives|

## Onboarding Prerequisites 
1️⃣ [Design Log Management Architecture](https://docs.microsoft.com/azure/azure-monitor/logs/design-logs-deployment)<br>
2️⃣ [Onboard Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard)<br>
3️⃣ [Connect & Ingest Data Sources](https://docs.microsoft.com/azure/sentinel/connect-data-sources)<br>
4️⃣ [Extend Microsoft Sentinel Across Workspaces and Tenants](https://docs.microsoft.com/azure/sentinel/extend-sentinel-across-workspaces-tenants)<br>
5️⃣ [Configure 12 Months Hot Path Storage with Data Retention](https://docs.microsoft.com/azure/azure-monitor/logs/data-retention-archive)<br>
6️⃣ [Configure 18 Months Cold Path Storage with Azure Data Explorer](https://docs.microsoft.com/azure/sentinel/store-logs-in-azure-data-explorer) & [Configure Basic Logs](https://docs.microsoft.com/azure/azure-monitor/logs/basic-logs-configure)<br>
7️⃣ [Onboard Microsoft Defender for Cloud](https://docs.microsoft.com/azure/security-center/security-center-get-started)<br>
8️⃣ [Add the Azure Security Benchmark and NIST SP 800-53 R4 Assessments to Your Dashboard](https://docs.microsoft.com/azure/security-center/update-regulatory-compliance-packages#add-a-regulatory-standard-to-your-dashboard)<br>
9️⃣ [Continuously Export Microsoft Defender for Cloud Security Recommendations to Microsoft Sentinel](https://docs.microsoft.com/azure/security-center/continuous-export)<br>

## Print/Export Report
1️⃣ Set Background Theme: Settings > Appearance > Theme: Azure > Apply<br>
2️⃣ Print/Export Report: More Content Actions (...) > Print Content<br>
3️⃣ Settings: Layout (Landscape), Pages (All), Print (One Sided), Scale (60), Pages Per Sheet (1), Quality (1,200 DPI), Margins (None) > Print<br>

## Workbook
The Microsoft Sentinel: Maturity Model for Event Log Management (M-21-31) workbook provides a dashboard for viewing log queries, azure resource graph, metrics, and policies aligned to logging requirements across the Microsoft portfolio including Azure, Microsoft 365, Multi-Cloud, Hybrid, and On-Premises workloads. This workbook enables Security Architects, Engineers, SecOps Analysts, Managers, and IT Pros to gain situational awareness visibility for the security posture of cloud workloads. There are also recommendations for selecting, designing, deploying, and configuring Microsoft offerings for alignment with respective M-21-31 requirements and practices.

## Hunting Queries
### 1) M2131_Recommended Datatable is not logged_Event Logging (EL0)
This alert audits your logging architecture for recommended data tables aligned to Event Logging (EL0) of the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when recommended data tables in EL0 are not present.<br>
### 2) M2131_Recommended Datatable is not logged_Basic Event Logging (EL1)
This alert audits your logging architecture for recommended data tables aligned to Basic Event Logging (EL1) of the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when recommended data tables in EL1 are not present.<br>
### 3) M2131_Recommended Datatable is not logged_Intermediate Event Logging (EL2)
This alert audits your logging architecture for recommended data tables aligned to Intermediate Event Logging (EL2) of the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when recommended data tables in EL2 are not present.<br>
### 4) M2131_Recommended Datatable is not logged_Advanced Event Logging (EL3)
This alert audits your logging architecture for recommended data tables aligned to Advanced Event Logging (EL3) of the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when recommended data tables in EL3 are not present.<br>

## Analytics
### 1) M2131_Recommended Datatable is unhealthy (last logged received drop)
This alert is designed to monitor recommended data tables aligned to the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when a recommended data table hasn't been observed in over 48 hours.<br>
### 2) M2131_Data Connector Added or Removed
This alert is designed to monitor data connector configurations. This alert is triggered when a data connector is added, updated, or deleted.<br>
### 3) M2131_Asset Stopped Logging (heartbeat)
This alert is designed to monitor assets within the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when a monitored asset fails to provide a heartbeat within 24 hours.<br>
### 4) M2131_Log Analytics Workspace: Active Storage is less than 12 Months
This alert is designed to monitor log retention within the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when a log analytics workspace in active storage is configured for less than 1 year.<br>
### 5) M2131_Event Log Management Posture Changed (Event Logging EL0)
This alert is designed to monitor Azure policies aligned with the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when EL0 policy compliance falls below 70% within a 1 week time-frame.<br>
### 6) M2131_Event Log Management Posture Changed (Basic Event Logging EL1)
This alert is designed to monitor Azure policies aligned with the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when EL1 policy compliance falls below 70% within a 1 week time-frame.<br>
### 7) M2131_Event Log Management Posture Changed (Intermediate Event Logging EL2)
This alert is designed to monitor Azure policies aligned with the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when EL2 policy compliance falls below 70% within a 1 week time-frame.<br>
### 8) M2131_Event Log Management Posture Changed (Advanced Event Logging EL3)
This alert is designed to monitor Azure policies aligned with the Maturity Model for Event Log Management (M-21-31) standard. The alert triggers when EL3 policy compliance falls below 70% within a 1 week time-frame.<br>

## Playbooks
### 1) Notify Log Management Team
This Security Orchestration, Automation, & Response (SOAR) capability is designed for configuration with the solution's analytics rules. When analytics rules trigger this automation notifies the log management team of respective details via Teams chat and exchange email. this automation reduces requirements to manually monitor the workbook or analytics rules while increasing response times.<br>
### 2) Open DevOps Task based on Recommendation
This Security Orchestration, Automation, & Response (SOAR) capability is designed to create an Azure DevOps Task when an ASC recommendation is triggered. This automation enables a consistent response when resources become unhealthy relative to a predefined recommendation, enabling teams to focus on remediation and improving response times.
### 3) Open JIRA Ticket based on Recommendation
This Security Orchestration, Automation, & Response (SOAR) capability is designed to open a Jira issue when an recommendation is unhealthy in Microsoft Defender for Cloud. This automation improves time to response by providing consistent notifications when resources become unhealthy relative to a predefined recommendation.

## Disclaimer
The Microsoft Sentinel Maturity Model for Event Log Management (M-21-31) Solution demonstrates best practice guidance, but Microsoft does not guarantee nor imply compliance. All accreditation requirements and decisions are governed by the 💡 [Office of Management and Budget](https://www.whitehouse.gov/wp-content/uploads/2021/08/M-21-31-Improving-the-Federal-Governments-Investigative-and-Remediation-Capabilities-Related-to-Cybersecurity-Incidents.pdf) as outlined in the Improving the Federal Government's Investigative and Remediation Capabilities Related to Cybersecurity Incidents Memorandum (M-21-31). This solution provides visibility and situational awareness for control requirements delivered with Microsoft technologies in predominantly cloud-based environments. Customer experience will vary by user and some panels may require additional configurations and query modification for operation. Recommendations do not imply coverage of respective controls as they are often one of several courses of action for approaching requirements which is unique to each customer. Recommendations should be considered a starting point for planning full or partial coverage of respective control requirements. 