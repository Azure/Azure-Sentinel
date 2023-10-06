# Overview
---
This solution enables SecOps Analysts, Threat Intelligence Professional, and Threat Hunters to gain situational awareness for threats in cloud environment. The Solution includes (2) Workbooks  designed to enable threat hunting programs. Threat modeling is an advanced discipline requiring a detailed understanding of adversary actions. Threat analysis provides an understanding of where the attacker is in the cycle which often drives both a historic lens of where the threat may have progressed, but also predictive analytics on the threat’s objectives. This approach is adversarial as understanding of the threat’s attack cycle drives defense actions in a red versus blue model. The Threat Analysis & Response Solution augments the customer burden of building threat hunting programs. <br>
<br>

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FThreatAnalysis%26Response%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FThreatAnalysis%26Response%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis%26Response/Workbooks/Images/ThreatAnalysis%26ResponseWhite1.png?raw=true)

## Getting Started Prerequisites
1️⃣ [Configure Analytics & Hunting with Microsoft Sentinel: MITRE Blade](https://docs.microsoft.com/azure/sentinel/mitre-coverage)<br>
2️⃣ [Onboard Microsoft Defender for Cloud](https://docs.microsoft.com/azure/defender-for-cloud/get-started)<br>
3️⃣ [Add the NIST SP 800-53 R4 Assessment to Your Dashboard](https://docs.microsoft.com/azure/security-center/update-regulatory-compliance-packages#add-a-regulatory-standard-to-your-dashboard)<br>
4️⃣ [Continuously Export Security Center Data: SecurityRegulatoryCompliance & SecurityRecommendation Data Tables](https://docs.microsoft.com/azure/security-center/continuous-export)<br>
5️⃣ [Review Security Coverage by the MITRE ATT&CK® Framework](https://docs.microsoft.com/azure/sentinel/mitre-coverage)<br>

## Print/Export Reports
1️⃣ Set Background Theme: Settings > Appearance > Theme: Azure > Apply<br>
2️⃣ Print/Export Report: More Content Actions (...) > Print Content<br>
3️⃣ Settings: Layout (Landscape), Pages (All), Print (One Sided), Scale (60), Pages Per Sheet (1), Quality (1,200 DPI), Margins (None) > Print<br>

## Workbooks
### 1) Threat Analysis & Response Workbook
This workbook provides the foundation for building a threat hunting program including references for analytics and hunting query repositories. There are data source statistics to baseline available data sets which is helpful in planning selection of analytics rules. There is a breakdown of ATT&CK tactics to understand focus areas for greater analysis. There is an assessment of detection platform services to understand which capabilities and workloads are being employed. <br>
### 2) Dynamic Threat Modeling Workbook
This workbook enables SecOps Analysts, Threat Intelligence Professionals, and Threat Hunters to gain situational awareness for threats in cloud, multi-cloud, hybrid, and on-premise environments. This solution is designed to augment staffing through automation, artificial intelligence, machine learning, alert generation, and visualizations. Threat modeling is an advanced cybersecurity discipline requiring detailed knowledge of identifying and acting on the attacker based on observation of indicators in various stages of the attack cycle. This offering provides granular situational awareness across the MITRE ATT&CK® for Cloud Matrix including 75+ Tactic/Technique cards demonstrating a red versus blue approach to threat modeling.<br>

## Disclaimer
This workbook demonstrates best practice guidance, but Microsoft does not guarantee nor imply compliance. All requirements, tactics, validations, and controls are governed by respective organizations. This solution provides visibility and situational awareness for security capabilities delivered with Microsoft technologies in predominantly cloud-based environments. Customer experience will vary by user and some panels may require additional configurations for operation. Recommendations do not imply coverage of respective controls as they are often one of several courses of action for approaching requirements which is unique to each customer. Recommendations should be considered a starting point for planning full or partial coverage of respective requirements. 
