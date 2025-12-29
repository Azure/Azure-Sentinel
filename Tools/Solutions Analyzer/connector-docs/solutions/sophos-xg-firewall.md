# Sophos XG Firewall

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Sophos XG Firewall](../connectors/sophosxgfirewall.md)

**Publisher:** Sophos

The [Sophos XG Firewall](https://www.sophos.com/products/next-gen-firewall.aspx) allows you to easily connect your Sophos XG Firewall logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigations. Integrating Sophos XG Firewall with Microsoft Sentinel provides more visibility into your organization's firewall traffic and will enhance security monitoring capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_SophosXGFirewall.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20XG%20Firewall/Data%20Connectors/Connector_Syslog_SophosXGFirewall.json) |

[→ View full connector details](../connectors/sophosxgfirewall.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Sophos XG Firewall](../connectors/sophosxgfirewall.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                  |
|-------------|--------------------------------|-------------------------------------------------------------------------------------|
| 3.0.1       | 09-12-2024                     | Rmoved Deprecated **Data Connector**                                                |
|             |                                | Updated SophosXGFirewall.json **Workbook** to fix missing fields                    |
| 3.0.0       | 01-08-2024                     | Update **Parser** as part of Syslog migration </br> Deprecating **Data Connectors** |

[← Back to Solutions Index](../solutions-index.md)
