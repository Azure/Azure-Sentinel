# Illusive Platform

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Illusive Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://illusive.com/support](https://illusive.com/support) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Illusive Platform via Legacy Agent](../connectors/illusiveattackmanagementsystem.md)

**Publisher:** illusive

The Illusive Platform Connector allows you to share Illusive's attack surface analysis data and incident logs with Microsoft Sentinel and view this information in dedicated dashboards that offer insight into your organization's attack surface risk (ASM Dashboard) and track unauthorized lateral movement in your organization's network (ADS Dashboard).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [illusive%20Attack%20Management%20System.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform/Data%20Connectors/illusive%20Attack%20Management%20System.json) |

[→ View full connector details](../connectors/illusiveattackmanagementsystem.md)

### [[Deprecated] Illusive Platform via AMA](../connectors/illusiveattackmanagementsystemama.md)

**Publisher:** illusive

The Illusive Platform Connector allows you to share Illusive's attack surface analysis data and incident logs with Microsoft Sentinel and view this information in dedicated dashboards that offer insight into your organization's attack surface risk (ASM Dashboard) and track unauthorized lateral movement in your organization's network (ADS Dashboard).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_IllusivePlatformAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform/Data%20Connectors/template_IllusivePlatformAMA.json) |

[→ View full connector details](../connectors/illusiveattackmanagementsystemama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Illusive Platform via AMA](../connectors/illusiveattackmanagementsystemama.md), [[Deprecated] Illusive Platform via Legacy Agent](../connectors/illusiveattackmanagementsystem.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 12-07-2024                     |    Deprecating data connector                                      |
| 3.0.0       | 13-09-2023                     |	Addition of new Illusive Platform AMA **Data Connector**        |

[← Back to Solutions Index](../solutions-index.md)
