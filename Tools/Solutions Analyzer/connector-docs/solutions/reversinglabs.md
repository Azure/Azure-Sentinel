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

## Tables Reference

This solution queries **2 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`DomainQuery`](../tables/domainquery.md) | Workbooks |
| [`ThreatIntelIndicatorsv2`](../tables/threatintelindicatorsv2.md) | Workbooks |

### Internal Tables

The following **3 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`RLTiCloudQuotas_CL`](../tables/rlticloudquotas-cl.md) | Playbooks (writes), Workbooks |
| [`SecurityAlert`](../tables/securityalert.md) | Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | Workbooks |

## Content Items

This solution includes **6 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 5 |
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ReversingLabs-CapabilitiesOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReversingLabs/Workbooks/ReversingLabs-CapabilitiesOverview.json) | [`DomainQuery`](../tables/domainquery.md)<br>[`ThreatIntelIndicatorsv2`](../tables/threatintelindicatorsv2.md)<br>*Internal use:*<br>[`RLTiCloudQuotas_CL`](../tables/rlticloudquotas-cl.md)<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ReversingLabs-CheckQuota](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReversingLabs/Playbooks/ReversingLabs-CheckQuota/azuredeploy.json) | This playbook will check your ReversingLabs TitaniumCloud API quota and provide usage details. To be... | *Internal use:*<br>[`RLTiCloudQuotas_CL`](../tables/rlticloudquotas-cl.md) *(write)* |
| [SpectraAnalyze-EnrichFileHash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReversingLabs/Playbooks/SpectraAnalyze-EnrichFileHash/azuredeploy.json) | This playbook will enrich a Microsoft Sentinel incident with file hash information from a Spectra An... | - |
| [SpectraAnalyze-EnrichNetworkEntities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReversingLabs/Playbooks/SpectraAnalyze-EnrichNetworkEntities/azuredeploy.json) | This playbook will enrich a network entities (IP addresses, URLs, and domain names) with information... | - |
| [SpectraIntelligence-EnrichFileHash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReversingLabs/Playbooks/SpectraIntelligence-EnrichFileHash/azuredeploy.json) | This playbook will enrich a Microsoft Sentinel Incident with file hash information from ReversingLab... | - |
| [SpectraIntelligence-EnrichNetworkEntities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReversingLabs/Playbooks/SpectraIntelligence-EnrichNetworkEntities/azuredeploy.json) | This playbook will enrich a Microsoft Sentinel Incident with information about network entities (IP ... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 08-08-2025                     | Updated Reversing Labs **workbook** with new ThreatIntelIndicators Table |
| 3.0.1       | 17-07-2024                     | **What's New** <br/> - Playbook \| SpectraAnalyze-EnrichNetworkEntities: New playbook that enriches network entities (IP addresses, URLs, and domain names) with data from a Spectra Analyze appliance \| v1.0.0<br/> - Playbook \| SpectraIntelligence-EnrichNetworkEntities: New playbook that enriches network entities (IP addresses, URLs, and domain names) with data from Spectra Intelligence. \| v1.0.0 <br/> - Playbook \| SpectraAnalyze-EnrichFileHash: New playbook exmaple for enriching file hash entities with data from a Spectra Analyze apliance \| v1.0.0 <br/> **What's Changed** <br/> - Playbook \| ReversingLabs-EnrichFileHash has been renamed to SpectraIntelligence-EnrichFileHash |
| 3.0.0       | 09-08-2023                     | **Playbook** \| ReversingLabs-EnrichFileHash: Updated to use new TitaniumCloud Logic App connector; Added AV scan results \| v2.0.0  <br/> **Workbook** \| ReversingLabs-CapabilitiesOverview: Remove hardcoded parameter value "ti_feed_check"; Update indicator quality query to be more accurate for uniqueness check \| v1.1.2 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
