# Illusive Platform

## Solution Information

| | |
|------------------------|-------|
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

### [[Deprecated] Illusive Platform via AMA](../connectors/illusiveattackmanagementsystemama.md)

**Publisher:** illusive

The Illusive Platform Connector allows you to share Illusive's attack surface analysis data and incident logs with Microsoft Sentinel and view this information in dedicated dashboards that offer insight into your organization's attack surface risk (ASM Dashboard) and track unauthorized lateral movement in your organization's network (ADS Dashboard).

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_IllusivePlatformAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform/Data%20Connectors/template_IllusivePlatformAMA.json) |

[→ View full connector details](../connectors/illusiveattackmanagementsystemama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Illusive Platform via AMA](../connectors/illusiveattackmanagementsystemama.md), [[Deprecated] Illusive Platform via Legacy Agent](../connectors/illusiveattackmanagementsystem.md) |

[← Back to Solutions Index](../solutions-index.md)
