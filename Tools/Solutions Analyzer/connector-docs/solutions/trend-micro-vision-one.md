# Trend Micro Vision One

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Trend Micro |
| **Support Tier** | Partner |
| **Support Link** | [https://success.trendmicro.com/dcx/s/?language=en_US](https://success.trendmicro.com/dcx/s/?language=en_US) |
| **Categories** | domains |
| **First Published** | 2022-05-11 |
| **Last Updated** | 2024-07-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Vision%20One](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Vision%20One) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Trend Vision One](../connectors/trendmicroxdr.md)

**Publisher:** Trend Micro

The [Trend Vision One](https://www.trendmicro.com/en_us/business/products/detection-response/xdr.html) connector allows you to easily connect your Workbench alert data with Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities. This gives you more insight into your organization's networks/systems and improves your security operation capabilities.



The Trend Vision One connector is supported in Microsoft Sentinel in the following regions: Australia East, Australia Southeast, Brazil South, Canada Central, Canada East, Central India, Central US, East Asia, East US, East US 2, France Central, Japan East, Korea Central, North Central US, North Europe, Norway East, South Africa North, South Central US, Southeast Asia, Sweden Central, Switzerland North, UAE North, UK South, UK West, West Europe, West US, West US 2, West US 3.

| | |
|--------------------------|---|
| **Tables Ingested** | `TrendMicro_XDR_OAT_CL` |
| | `TrendMicro_XDR_RCA_Result_CL` |
| | `TrendMicro_XDR_RCA_Task_CL` |
| | `TrendMicro_XDR_WORKBENCH_CL` |
| **Connector Definition Files** | [TrendMicroXDR.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Vision%20One/Data%20Connectors/TrendMicroXDR.json) |

[→ View full connector details](../connectors/trendmicroxdr.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `TrendMicro_XDR_OAT_CL` | [Trend Vision One](../connectors/trendmicroxdr.md) |
| `TrendMicro_XDR_RCA_Result_CL` | [Trend Vision One](../connectors/trendmicroxdr.md) |
| `TrendMicro_XDR_RCA_Task_CL` | [Trend Vision One](../connectors/trendmicroxdr.md) |
| `TrendMicro_XDR_WORKBENCH_CL` | [Trend Vision One](../connectors/trendmicroxdr.md) |

[← Back to Solutions Index](../solutions-index.md)
