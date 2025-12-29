# Trend Micro Apex One

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

The [Trend Micro Apex One](https://www.trendmicro.com/en_us/business/products/user-protection/sps/endpoint.html) data connector provides the capability to ingest [Trend Micro Apex One events](https://aka.ms/sentinel-TrendMicroApex-OneEvents) into Microsoft Sentinel. Refer to [Trend Micro Apex Central](https://aka.ms/sentinel-TrendMicroApex-OneCentral) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [TrendMicro_ApexOne.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Data%20Connectors/TrendMicro_ApexOne.json) |

[→ View full connector details](../connectors/trendmicroapexone.md)

### [[Deprecated] Trend Micro Apex One via AMA](../connectors/trendmicroapexoneama.md)

**Publisher:** Trend Micro

The [Trend Micro Apex One](https://www.trendmicro.com/en_us/business/products/user-protection/sps/endpoint.html) data connector provides the capability to ingest [Trend Micro Apex One events](https://aka.ms/sentinel-TrendMicroApex-OneEvents) into Microsoft Sentinel. Refer to [Trend Micro Apex Central](https://aka.ms/sentinel-TrendMicroApex-OneCentral) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_TrendMicro_ApexOneAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Data%20Connectors/template_TrendMicro_ApexOneAMA.json) |

[→ View full connector details](../connectors/trendmicroapexoneama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Trend Micro Apex One via AMA](../connectors/trendmicroapexoneama.md), [[Deprecated] Trend Micro Apex One via Legacy Agent](../connectors/trendmicroapexone.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 13-12-2024                     |  Removed Deprecated **Data  Connectors**                           |
| 3.0.2 	  | 12-07-2024 					   |  Deprecated **Data Connector** 									|
| 3.0.1       | 25-10-2023                     |  **Hunting Query** column corrected                                |   
| 3.0.0       | 22-09-2023                     |  Addition of new Trend Micro Apex One AMA **Data connector**       | 	                                                            |

[← Back to Solutions Index](../solutions-index.md)
