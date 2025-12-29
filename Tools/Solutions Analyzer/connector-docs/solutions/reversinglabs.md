# ReversingLabs

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | ReversingLabs |
| **Support Tier** | Partner |
| **Support Link** | [https://support.reversinglabs.com/hc/en-us](https://support.reversinglabs.com/hc/en-us) |
| **Categories** | domains |
| **First Published** | 2022-08-08 |
| **Last Updated** | 2024-07-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReversingLabs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReversingLabs) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 08-08-2025                     | Updated Reversing Labs **workbook** with new ThreatIntelIndicators Table |
| 3.0.1       | 17-07-2024                     | **What's New** <br/> - Playbook \| SpectraAnalyze-EnrichNetworkEntities: New playbook that enriches network entities (IP addresses, URLs, and domain names) with data from a Spectra Analyze appliance \| v1.0.0<br/> - Playbook \| SpectraIntelligence-EnrichNetworkEntities: New playbook that enriches network entities (IP addresses, URLs, and domain names) with data from Spectra Intelligence. \| v1.0.0 <br/> - Playbook \| SpectraAnalyze-EnrichFileHash: New playbook exmaple for enriching file hash entities with data from a Spectra Analyze apliance \| v1.0.0 <br/> **What's Changed** <br/> - Playbook \| ReversingLabs-EnrichFileHash has been renamed to SpectraIntelligence-EnrichFileHash |
| 3.0.0       | 09-08-2023                     | **Playbook** \| ReversingLabs-EnrichFileHash: Updated to use new TitaniumCloud Logic App connector; Added AV scan results \| v2.0.0  <br/> **Workbook** \| ReversingLabs-CapabilitiesOverview: Remove hardcoded parameter value "ti_feed_check"; Update indicator quality query to be more accurate for uniqueness check \| v1.1.2 |

[← Back to Solutions Index](../solutions-index.md)
