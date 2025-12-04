# Prancer PenSuiteAI Integration

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Prancer PenSuiteAI Integration |
| **Support Tier** | Partner |
| **Support Link** | [https://www.prancer.io](https://www.prancer.io) |
| **Categories** | domains |
| **First Published** | 2023-08-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Prancer Data Connector](../connectors/prancerlogdata.md)

**Publisher:** Prancer

The Prancer Data Connector has provides the capability to ingest Prancer (CSPM)[https://docs.prancer.io/web/CSPM/] and [PAC](https://docs.prancer.io/web/PAC/introduction/) data to process through Microsoft Sentinel. Refer to [Prancer Documentation](https://docs.prancer.io/web) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `prancer_CL` |
| **Connector Definition Files** | [PrancerLogData.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Data%20Connectors/PrancerLogData.json) |

[→ View full connector details](../connectors/prancerlogdata.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `prancer_CL` | [Prancer Data Connector](../connectors/prancerlogdata.md) |

[← Back to Solutions Index](../solutions-index.md)
