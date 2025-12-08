# Trend Micro Apex One

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-06 |
| **Last Updated** | 2022-03-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Trend Micro Apex One via Legacy Agent](../connectors/trendmicroapexone.md)

**Publisher:** Trend Micro

### [[Deprecated] Trend Micro Apex One via AMA](../connectors/trendmicroapexoneama.md)

**Publisher:** Trend Micro

The [Trend Micro Apex One](https://www.trendmicro.com/en_us/business/products/user-protection/sps/endpoint.html) data connector provides the capability to ingest [Trend Micro Apex One events](https://aka.ms/sentinel-TrendMicroApex-OneEvents) into Microsoft Sentinel. Refer to [Trend Micro Apex Central](https://aka.ms/sentinel-TrendMicroApex-OneCentral) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_TrendMicro_ApexOneAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Data%20Connectors/template_TrendMicro_ApexOneAMA.json) |

[→ View full connector details](../connectors/trendmicroapexoneama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Trend Micro Apex One via AMA](../connectors/trendmicroapexoneama.md), [[Deprecated] Trend Micro Apex One via Legacy Agent](../connectors/trendmicroapexone.md) |

[← Back to Solutions Index](../solutions-index.md)
