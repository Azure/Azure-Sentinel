# Keeper Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Keeper Security |
| **Support Tier** | Partner |
| **Support Link** | [https://www.keepersecurity.com](https://www.keepersecurity.com) |
| **Categories** | domains |
| **First Published** | 2025-06-03 |
| **Last Updated** | 2025-06-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Keeper Security Push Connector](../connectors/keepersecuritypush2.md)

**Publisher:** Keeper Security

The [Keeper Security](https://keepersecurity.com) connector provides the capability to read raw event data from Keeper Security in Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `KeeperSecurityEventNewLogs_CL` |
| **Connector Definition Files** | [KepperSecurity_Definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security/Data%20Connectors/KeeperSecurity_ccp/KepperSecurity_Definition.json) |

[→ View full connector details](../connectors/keepersecuritypush2.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `KeeperSecurityEventNewLogs_CL` | [Keeper Security Push Connector](../connectors/keepersecuritypush2.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                     |
|-------------|--------------------------------|----------------------------------------|
| 3.0.1       | 25-07-2025                     | Added new **Analytic Rules** and **Workbook**  |
| 3.0.0       | 11-06-2025                     | Initial Solution Release with KeeperSecurity **Data Connector** CCP. |

[← Back to Solutions Index](../solutions-index.md)
