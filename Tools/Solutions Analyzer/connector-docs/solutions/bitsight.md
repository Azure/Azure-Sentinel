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

This solution provides **1 data connector(s)**.

### [Bitsight data connector](../connectors/bitsight.md)

**Publisher:** BitSight Technologies, Inc.

The [BitSight](https://www.BitSight.com/) Data Connector supports evidence-based cyber risk monitoring by bringing BitSight data in Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `BitsightAlerts_data_CL` |
| | `BitsightBreaches_data_CL` |
| | `BitsightCompany_details_CL` |
| | `BitsightCompany_rating_details_CL` |
| | `BitsightDiligence_historical_statistics_CL` |
| | `BitsightDiligence_statistics_CL` |
| | `BitsightFindings_data_CL` |
| | `BitsightFindings_summary_CL` |
| | `BitsightGraph_data_CL` |
| | `BitsightIndustrial_statistics_CL` |
| | `BitsightObservation_statistics_CL` |
| **Connector Definition Files** | [BitSight_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Data%20Connectors/BitSightDataConnector/BitSight_API_FunctionApp.json) |

[→ View full connector details](../connectors/bitsight.md)

## Tables Reference

This solution ingests data into **11 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BitsightAlerts_data_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightBreaches_data_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightCompany_details_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightCompany_rating_details_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightDiligence_historical_statistics_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightDiligence_statistics_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightFindings_data_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightFindings_summary_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightGraph_data_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightIndustrial_statistics_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightObservation_statistics_CL` | [Bitsight data connector](../connectors/bitsight.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.1.0       | 28-07-2025                     | Updated the python runtime version to 3.12. Added support for Log Ingestion API and updated parsers accordingly                          |
| 3.0.2       | 26-07-2024                     | Update **Analytic rules** for missing TTP                          |
| 3.0.1       | 15-04-2024                     | Added Bitsight prefix in data tables name                           |
| 3.0.0       | 23-01-2024                     | Updated **Data Connector** code with the fix of Pagination and Checkpoint related issue |

[← Back to Solutions Index](../solutions-index.md)
