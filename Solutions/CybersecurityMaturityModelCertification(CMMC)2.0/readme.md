# Overview
---
The Microsoft Sentinel: Cybersecurity Maturity Model Certification (CMMC) 2.0 Solution provides a mechanism for viewing log queries aligned to CMMC 2.0 requirements across the Microsoft portfolio. This solution enables governance and compliance teams to design, build, monitor, and respond to CMMC 2.0 requirements across 25+ Microsoft products. The solution includes the new CMMC 2.0 Workbook, (2) Analytics Rules, and (1) Playbook. While only Microsoft Sentinel is required to get started, the solution is enhanced with numerous Microsoft offerings. This Solution enables Security Architects, Engineers, SecOps Analysts, Managers, and IT Pros to gain situational awareness visibility for the security posture of cloud workloads. There are also recommendations for selecting, designing, deploying, and configuring Microsoft offerings for alignment with respective security best practice. 

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCybersecurityMaturityModelCertification(CMMC)2.0%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCybersecurityMaturityModelCertification(CMMC)2.0%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](./CybersecurityMaturityModelCertification(CMMC)Workbook.png)

# Getting Started
This Solution is designed to augment staffing through automation, artificial intelligence, machine learning, query/alerting generation, and visualizations. This workbook leverages Azure Policy, Azure Resource Graph, and Azure Log Analytics to align with Cybersecurity Maturity Model Certification 2.0 control requirements. A filter set is available for custom reporting by guides, subscriptions, workspaces, time-filtering, control family, and level. This offering telemetry from 50+ Microsoft Security products, while only Microsoft Sentinel/Microsoft Defender for Cloud are required to get started, each offering provides additional enrichment for aligning with control requirements. Each CMMC control includes a Control Card detailing an overiew of requirements, primary/secondary controls, deep-links to referenced product pages/portals, recommendations, implementation guides, compliance cross-walks and tooling telemetry for building situational awareness of cloud workloads. 
💡 [Deploy Azure CMMC Blueprint](https://docs.microsoft.com/azure/governance/blueprints/samples/cmmc-l3)<br>
💡 [Onboard Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard)<br>
💡 [Onboard Microsoft Defender for Cloud](https://docs.microsoft.com/azure/security-center/security-center-get-started)<br>
💡 [Add the Microsoft Defender for Cloud: NIST SP 800 171 R2 Assessment to Your Dashboard](https://docs.microsoft.com/azure/security-center/update-regulatory-compliance-packages#add-a-regulatory-standard-to-your-dashboard)<br>
💡 [Continuously Export Security Center Data to Log Analytics Workspace](https://docs.microsoft.com/azure/security-center/continuous-export)<br>
💡 [Extend Microsoft Sentinel Across Workspaces and Tenants](https://docs.microsoft.com/azure/sentinel/extend-sentinel-across-workspaces-tenants)<br>

# Workbook
The Microsoft Sentinel CMMC 2.0 Workbook provides a mechanism for viewing log queries, azure resource graph, and policies aligned to CMMC controls across the Microsoft portfolio including Microsoft security offerings, Office 365, Teams, and many more. This workbook enables Security Architects, Engineers, SecOps Analysts, Managers, and IT Pros to gain situational awareness visibility for the security posture of cloud workloads. There are also recommendations for selecting, designing, deploying, and configuring Microsoft offerings for alignment with respective CMMC 2.0 requirements and practices.

# Analytics Rules
The Microsoft Sentinel: CMMC 2.0 Analytics rules leverage Microsoft Defender for Cloud Regulatory Compliance mappings (Derived from NIST SP 800-171) to measure CMMC 2.0 alignment across Level 1 (Foundation) and Level 2 (Advanced) requirements. The default configuration is set for scheduled rules running every 7 days to reduce alert overload. The default configuration is to alert when posture compliance is below 70% and this number is configurable per organizational requirements. 

# Playbooks
The Microsoft Sentinel: CMMC 2.0 Solution includes a PlaybookaAutomation for Security Orchestration Automation & Response (SOAR). This playbook is triggered when an Microsoft Sentinel incident is generated, resulting in an email and Teams chat to the Security Governance Team including respective details of the event and remediation options. Note, this automation requires configuration for Security Governance Team group email address and Teams channel. There is also a requirement to configure this automation rule to trigger for each CMMC 2.0 Analytics Rule to ensure the governance team is notified for remediation accordingly.  

## Disclaimer
The Microsoft Sentinel CMMC 2.0 Solution demonstrates best practice guidance, but Microsoft does not guarantee nor imply compliance. The workbook outlines controls across Levels 1-2. All accreditation requirements and decisions are governed by the 💡[CMMC Accreditation Body](https://www.cmmcab.org/c3pao-lp). This solution provides visibility and situational awareness for control requirements delivered with Microsoft technologies in predominantly cloud-based environments. Customer experience will vary by user and some panels may require additional configurations and query modification for operation. Recommendations should be considered a starting point for planning full or partial coverage of respective control requirements. 