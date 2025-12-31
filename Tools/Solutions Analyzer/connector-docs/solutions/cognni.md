# Cognni

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cognni |
| **Support Tier** | Partner |
| **Support Link** | [https://cognni.ai/contact-support/](https://cognni.ai/contact-support/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Cognni](../connectors/cognnisentineldataconnector.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) | [Cognni](../connectors/cognnisentineldataconnector.md) | Analytics, Workbooks |

## Content Items

This solution includes **16 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 15 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Cognni Incidents for Highly Sensitive Business Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniHighRiskBusinessIncidents.yaml) | High | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Highly Sensitive Financial Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniHighRiskFinancialIncidents.yaml) | High | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Highly Sensitive Governance Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniHighRiskGovernanceIncidents.yaml) | High | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Highly Sensitive HR Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniHighRiskHRIncidents.yaml) | High | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Highly Sensitive Legal Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniHighRiskLegalIncidents.yaml) | High | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Low Sensitivity Business Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniLowRiskBusinessIncidents.yaml) | Low | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Low Sensitivity Financial Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniLowRiskFinancialIncidents.yaml) | Low | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Low Sensitivity Governance Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniLowRiskGovernanceIncidents.yaml) | Low | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Low Sensitivity HR Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniLowRiskHRIncidents.yaml) | Low | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Low Sensitivity Legal Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniLowRiskLegalIncidents.yaml) | Low | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Medium Sensitivity Business Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniMediumRiskBusinessIncidents.yaml) | Medium | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Medium Sensitivity Financial Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniMediumRiskFinancialIncidents.yaml) | Medium | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Medium Sensitivity Governance Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniMediumRiskGovernanceIncidents.yaml) | Medium | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Medium Sensitivity HR Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniMediumRiskHRIncidents.yaml) | Medium | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |
| [Cognni Incidents for Medium Sensitivity Legal Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Analytic%20Rules/CognniMediumRiskLegalIncidents.yaml) | Medium | Collection | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CognniIncidentsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Workbooks/CognniIncidentsWorkbook.json) | [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
