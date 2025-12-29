# Trend Micro Deep Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Trend Micro |
| **Support Tier** | Partner |
| **Support Link** | [https://success.trendmicro.com/dcx/s/?language=en_US](https://success.trendmicro.com/dcx/s/?language=en_US) |
| **Categories** | domains |
| **First Published** | 2022-05-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Deep%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Deep%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Trend Micro Deep Security via Legacy](../connectors/trendmicro.md)

**Publisher:** Trend Micro

The Trend Micro Deep Security connector allows you to easily connect your Deep Security logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's networks/systems and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [TrendMicroDeepSecurity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Deep%20Security/Data%20Connectors/TrendMicroDeepSecurity.json) |

[→ View full connector details](../connectors/trendmicro.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Trend Micro Deep Security via Legacy](../connectors/trendmicro.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 03-01-2025                     | Removed Deprecated **Data connector**                              |
| 3.0.0       | 27-06-2024                     | Deprecating data connectors     |
| 2.0.1       | 11-11-2022                     | Updated OfferId     |
| 2.0.0       | 20-07-2022                     | Initial Package     |

[← Back to Solutions Index](../solutions-index.md)
