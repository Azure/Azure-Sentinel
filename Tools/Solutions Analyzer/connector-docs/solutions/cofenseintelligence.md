# CofenseIntelligence

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cofense Support |
| **Support Tier** | Partner |
| **Support Link** | [https://cofense.com/contact-support/](https://cofense.com/contact-support/) |
| **Categories** | domains |
| **First Published** | 2023-05-26 |
| **Last Updated** | 2024-05-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseIntelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseIntelligence) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Cofense Intelligence Threat Indicators Ingestion](../connectors/cofenseintelligence.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Malware_Data_CL`](../tables/malware-data-cl.md) | [Cofense Intelligence Threat Indicators Ingestion](../connectors/cofenseintelligence.md) | Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | [Cofense Intelligence Threat Indicators Ingestion](../connectors/cofenseintelligence.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CofenseIntelligenceThreatIndicators](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseIntelligence/Workbooks/CofenseIntelligenceThreatIndicators.json) | [`Malware_Data_CL`](../tables/malware-data-cl.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 10-12-2022                     | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
