# SymantecProxySG

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2021-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Symantec ProxySG](../connectors/symantecproxysg.md)

**Publisher:** Symantec

The [Symantec ProxySG](https://www.broadcom.com/products/cyber-security/network/gateway/proxy-sg-and-advanced-secure-gateway) allows you to easily connect your Symantec ProxySG logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigations. Integrating Symantec ProxySG with Microsoft Sentinel provides more visibility into your organization's network proxy traffic and will enhance security monitoring capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_SymantecProxySG.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG/Data%20Connectors/Connector_Syslog_SymantecProxySG.json) |

[→ View full connector details](../connectors/symantecproxysg.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Symantec ProxySG](../connectors/symantecproxysg.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       | 20-01-2025                     | Removed Custom Entity mappings from **Analytic rules**          |
| 3.0.2       | 24-12-2024                     |Removed Deprecated **Data Connector**        |
| 3.0.1       | 01-08-2024                     |Update **Parser** as part of Syslog migration                         |
|             |                                |Deprecating data connectors                                           |
| 3.0.0       | 06-11-2023                     | Modified the **Data Connector** with improved onboarding instructions and Optimized the **Parser** to process the logs with improved performance |

[← Back to Solutions Index](../solutions-index.md)
