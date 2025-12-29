# Symantec VIP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20VIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20VIP) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Symantec VIP](../connectors/symantecvip.md)

**Publisher:** Symantec

The [Symantec VIP](https://vip.symantec.com/) connector allows you to easily connect your Symantec VIP logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_SymantecVIP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20VIP/Data%20Connectors/Connector_Syslog_SymantecVIP.json) |

[→ View full connector details](../connectors/symantecvip.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Symantec VIP](../connectors/symantecvip.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.2       | 20-01-2025                     | Removed Custom Entity mappings from **Analytic rules**          |
| 3.0.1       | 31-12-2024                     | Removed Deprecated **Data connector**          |
| 3.0.0       | 01-08-2024                     | Update **Parser** as part of Syslog migration  |
|             |                                | Deprecating data connectors                    |

[← Back to Solutions Index](../solutions-index.md)
