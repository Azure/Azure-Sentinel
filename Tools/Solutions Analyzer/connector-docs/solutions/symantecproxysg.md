# SymantecProxySG

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_SymantecProxySG.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG/Data%20Connectors/Connector_Syslog_SymantecProxySG.json) |

[→ View full connector details](../connectors/symantecproxysg.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Symantec ProxySG](../connectors/symantecproxysg.md) |

[← Back to Solutions Index](../solutions-index.md)
