# BitSight

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
