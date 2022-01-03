# Overview
---
## What is the Cybersecurity Maturity Model Certification?
The Cybersecurity Maturity Model Certification (CMMC) model consists of maturity processes and cybersecurity best practices from multiple cybersecurity standards, frameworks, and other references, as well as inputs from the Defense Industrial Base (DIB) and Department of Defense (DoD stakeholders. The CMMC model specifies 5 levels of maturity measurement from Maturity Level 1 (Basic Cyber Hygiene) to Maturity Level 5 (Proactive & Advanced Cyber Practice). For more information, see the Office of the Under Secretary of Defense for Acquisition & Sustainment 💡[CMMC Model](https://www.acq.osd.mil/cmmc/draft.html).

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCybersecurityMaturityModelCertification(CMMC)%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCybersecurityMaturityModelCertification(CMMC)%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification(CMMC)/Workbooks/Images/CybersecurityMaturityModelCertification(CMMC)Black1.png?raw=true)


# Getting Started
This Solution is designed to augment staffing through automation, artificial intelligence, machine learning, query/alerting generation, and visualizations. This workbook leverages Azure Policy, Azure Resource Graph, and Azure Log Analytics to align with Cybersecurity Maturity Model Certification control requirements. A filter set is available for custom reporting by guides, subscriptions, workspaces, time-filtering, control family, and maturity level. This offering telemetry from 50+ Microsoft Security products, while only Microsoft Sentinel/Azure Security Center are required to get started, each offering provides additional enrichment for aligning with control requirements. Each CMMC control includes a Control Card detailing an overview of requirements, primary/secondary controls, deep-links to referenced product pages/portals, recommendations, implementation guides, compliance cross-walks and tooling telemetry for building situational awareness of cloud workloads. 
💡 [Deploy Azure CMMC Blueprint](https://docs.microsoft.com/azure/governance/blueprints/samples/cmmc-l3)<br>
💡 [Onboard Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard)<br>
💡 [Onboard Azure Security Center](https://docs.microsoft.com/azure/security-center/security-center-get-started)<br>
💡 [Add the Azure Security Center: CMMC Assessment to Your Dashboard](https://docs.microsoft.com/azure/security-center/update-regulatory-compliance-packages#add-a-regulatory-standard-to-your-dashboard)<br>
💡 [Continuously Export Security Center Data to Log Analytics Workspace](https://docs.microsoft.com/azure/security-center/continuous-export)<br>
💡 [Extend Microsoft Sentinel Across Workspaces and Tenants](https://docs.microsoft.com/azure/sentinel/extend-sentinel-across-workspaces-tenants)<br>

# Workbook
The Microsoft Sentinel CMMC Workbook provides a mechanism for viewing log queries, azure resource graph, and policies aligned to CMMC controls across the Microsoft portfolio including Microsoft security offerings, Office 365, Teams, and many more. This workbook enables Security Architects, Engineers, SecOps Analysts, Managers, and IT Pros to gain situational awareness visibility for the security posture of cloud workloads. There are also recommendations for selecting, designing, deploying, and configuring Microsoft offerings for alignment with respective CMMC requirements and practices.

# Analytics
The Microsoft Sentinel CMMC Analytics Rules include 10 Alerts designed to monitor CMMC compliance posture. The Alerts are organized by CMMC Control Family and leverage the Azure Security Center: SecurityRecommendation data source. Organizations can customize these alerts for time, subscription, workspace, maturity level, and compliance thresholds. These analytics allow security practitioners to actively monitor/alert on changes to CMMC compliance posture. 

# Playbook
This solution includes the Notify-Governance Compliance Team playbook. Playbooks are a Security Orchestration, Automation, & Response (SOAR) capability to automate manual tasks. This playbook should be configured as an automation action with the CMMC Analytics Rules. Upon triggering an Analytic Rule, this playbook captures respective details and both emails and posts a message in a Teams chat to the governance team. This automation increases response times while reducing the need to return to the workbook for monitoring. 