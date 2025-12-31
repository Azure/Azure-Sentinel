# ThreatAnalysis&Response

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis%26Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis%26Response) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **7 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AzureActivity`](../tables/azureactivity.md) | Workbooks |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Workbooks |
| [`MSFTBuiltinAlerts`](../tables/msftbuiltinalerts.md) | Workbooks |
| [`SecurityRegulatoryCompliance`](../tables/securityregulatorycompliance.md) | Workbooks |
| [`SentinelGithub`](../tables/sentinelgithub.md) | Workbooks |
| [`Usage`](../tables/usage.md) | Workbooks |
| [`securityresources`](../tables/securityresources.md) | Workbooks |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 2 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [DynamicThreatModeling&Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis%26Response/Workbooks/DynamicThreatModeling%26Response.json) | [`AzureActivity`](../tables/azureactivity.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`SecurityRegulatoryCompliance`](../tables/securityregulatorycompliance.md)<br>[`securityresources`](../tables/securityresources.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |
| [ThreatAnalysis&Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis%26Response/Workbooks/ThreatAnalysis%26Response.json) | [`MSFTBuiltinAlerts`](../tables/msftbuiltinalerts.md)<br>[`SentinelGithub`](../tables/sentinelgithub.md)<br>[`Usage`](../tables/usage.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |

## Additional Documentation

> 📄 *Source: [ThreatAnalysis&Response/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis&Response/README.md)*

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

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**    |
|-------------|--------------------------------|-----------------------|
| 3.0.1       | 01-09-2025                     | Updated the Threat Analysis & Response workbook to view in graphical view.  |
| 3.0.0       | 11-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
