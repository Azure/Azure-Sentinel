# Trend Micro TippingPoint

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Trend Micro |
| **Support Tier** | Partner |
| **Support Link** | [https://success.trendmicro.com/dcx/s/contactus?language=en_US](https://success.trendmicro.com/dcx/s/contactus?language=en_US) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20TippingPoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20TippingPoint) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Trend Micro TippingPoint via Legacy](../connectors/trendmicrotippingpoint.md)

**Publisher:** Trend Micro

The Trend Micro TippingPoint connector allows you to easily connect your TippingPoint SMS IPS events with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's networks/systems and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [TrendMicroTippingPoint.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20TippingPoint/Data%20Connectors/TrendMicroTippingPoint.json) |

[→ View full connector details](../connectors/trendmicrotippingpoint.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Trend Micro TippingPoint via Legacy](../connectors/trendmicrotippingpoint.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 06-01-2025                     | Removed Deprecated **Data connector**                              |
| 3.0.0       | 27-06-2024                     | Deprecating data connectors                                        |
| 2.0.2       | 30-05-2023                     | Updated Package                                                    |
| 2.0.1       | 11-11-2022                     | Initial Release                                                    |

[← Back to Solutions Index](../solutions-index.md)
