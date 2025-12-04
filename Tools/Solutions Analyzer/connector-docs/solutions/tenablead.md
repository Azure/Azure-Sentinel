# TenableAD

## Solution Information

| | |
|------------------------|-------|
| **Publisher** |  |
| **Support Tier** |  |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Tenable.ad](../connectors/tenable.ad.md)

**Publisher:** Tenable

Tenable.ad connector allows to export Tenable.ad Indicators of Exposures, trailflow and Indicators of Attacks logs to Azure Sentinel in real time.

It provides a data parser to manipulate the logs more easily. The different workbooks ease your Active Directory monitoring and provide different ways to visualize the data. The analytic templates allow to automate responses regarding different events, exposures, or attacks.

| | |
|--------------------------|---|
| **Tables Ingested** | `Tenable_ad_CL` |
| **Connector Definition Files** | [Tenable.ad.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Data%20Connectors/Tenable.ad.json) |

[→ View full connector details](../connectors/tenable.ad.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Tenable_ad_CL` | [Tenable.ad](../connectors/tenable.ad.md) |

[← Back to Solutions Index](../solutions-index.md)
