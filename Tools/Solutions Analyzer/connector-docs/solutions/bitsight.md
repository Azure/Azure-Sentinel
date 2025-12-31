# BitSight

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | BitSight Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.bitsight.com/customer-success-support](https://www.bitsight.com/customer-success-support) |
| **Categories** | domains |
| **First Published** | 2023-02-20 |
| **Last Updated** | 2024-02-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Bitsight data connector](../connectors/bitsight.md)

## Tables Reference

This solution uses **11 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`BitsightAlerts_data_CL`](../tables/bitsightalerts-data-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | Analytics |
| [`BitsightBreaches_data_CL`](../tables/bitsightbreaches-data-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | Analytics |
| [`BitsightCompany_details_CL`](../tables/bitsightcompany-details-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | Workbooks |
| [`BitsightCompany_rating_details_CL`](../tables/bitsightcompany-rating-details-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | - |
| [`BitsightDiligence_historical_statistics_CL`](../tables/bitsightdiligence-historical-statistics-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | Workbooks |
| [`BitsightDiligence_statistics_CL`](../tables/bitsightdiligence-statistics-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | - |
| [`BitsightFindings_data_CL`](../tables/bitsightfindings-data-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | Analytics, Workbooks |
| [`BitsightFindings_summary_CL`](../tables/bitsightfindings-summary-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | Workbooks |
| [`BitsightGraph_data_CL`](../tables/bitsightgraph-data-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | Analytics, Workbooks |
| [`BitsightIndustrial_statistics_CL`](../tables/bitsightindustrial-statistics-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | - |
| [`BitsightObservation_statistics_CL`](../tables/bitsightobservation-statistics-cl.md) | [Bitsight data connector](../connectors/bitsight.md) | - |

## Content Items

This solution includes **18 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 11 |
| Analytic Rules | 6 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [BitSight - compromised systems detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Analytic%20Rules/BitSightCompromisedSystemsDetected.yaml) | Medium | Execution | [`BitsightFindings_data_CL`](../tables/bitsightfindings-data-cl.md) |
| [BitSight - diligence risk category detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Analytic%20Rules/BitSightDiligenceRiskCategoryDetected.yaml) | Medium | Execution, Reconnaissance | [`BitsightFindings_data_CL`](../tables/bitsightfindings-data-cl.md) |
| [BitSight - drop in company ratings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Analytic%20Rules/BitSightDropInCompanyRatings.yaml) | High | Reconnaissance, CommandAndControl | [`BitsightGraph_data_CL`](../tables/bitsightgraph-data-cl.md) |
| [BitSight - drop in the headline rating](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Analytic%20Rules/BitSightDropInHeadlineRating.yaml) | High | Reconnaissance, CommandAndControl | [`BitsightGraph_data_CL`](../tables/bitsightgraph-data-cl.md) |
| [BitSight - new alert found](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Analytic%20Rules/BitSightNewAlertFound.yaml) | High | Impact, InitialAccess | [`BitsightAlerts_data_CL`](../tables/bitsightalerts-data-cl.md) |
| [BitSight - new breach found](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Analytic%20Rules/BitSightNewBreachFound.yaml) | Medium | Impact, InitialAccess | [`BitsightBreaches_data_CL`](../tables/bitsightbreaches-data-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [BitSightWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Workbooks/BitSightWorkbook.json) | [`BitsightCompany_details_CL`](../tables/bitsightcompany-details-cl.md)<br>[`BitsightDiligence_historical_statistics_CL`](../tables/bitsightdiligence-historical-statistics-cl.md)<br>[`BitsightFindings_data_CL`](../tables/bitsightfindings-data-cl.md)<br>[`BitsightFindings_summary_CL`](../tables/bitsightfindings-summary-cl.md)<br>[`BitsightGraph_data_CL`](../tables/bitsightgraph-data-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [BitSightAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightAlerts.yaml) | - | - |
| [BitSightBreaches](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightBreaches.yaml) | - | - |
| [BitSightCompanyDetails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightCompanyDetails.yaml) | - | - |
| [BitSightCompanyRatings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightCompanyRatings.yaml) | - | - |
| [BitSightDiligenceHistoricalStatistics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightDiligenceHistoricalStatistics.yaml) | - | - |
| [BitSightDiligenceStatistics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightDiligenceStatistics.yaml) | - | - |
| [BitSightFindingsData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightFindingsData.yaml) | - | - |
| [BitSightFindingsSummary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightFindingsSummary.yaml) | - | - |
| [BitSightGraphData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightGraphData.yaml) | - | - |
| [BitSightIndustrialStatistics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightIndustrialStatistics.yaml) | - | - |
| [BitSightObservationStatistics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Parsers/BitSightObservationStatistics.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.1.0       | 28-07-2025                     | Updated the python runtime version to 3.12. Added support for Log Ingestion API and updated parsers accordingly                          |
| 3.0.2       | 26-07-2024                     | Update **Analytic rules** for missing TTP                          |
| 3.0.1       | 15-04-2024                     | Added Bitsight prefix in data tables name                           |
| 3.0.0       | 23-01-2024                     | Updated **Data Connector** code with the fix of Pagination and Checkpoint related issue |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
