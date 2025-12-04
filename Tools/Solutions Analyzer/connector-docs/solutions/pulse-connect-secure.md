# Pulse Connect Secure

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Pulse Connect Secure](../connectors/pulseconnectsecure.md)

**Publisher:** Pulse Secure

The [Pulse Connect Secure](https://www.pulsesecure.net/products/pulse-connect-secure/) connector allows you to easily connect your Pulse Connect Secure logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigations. Integrating Pulse Connect Secure with Microsoft Sentinel provides more insight into your organization's network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_PulseConnectSecure.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure/Data%20Connectors/Connector_Syslog_PulseConnectSecure.json) |

[→ View full connector details](../connectors/pulseconnectsecure.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Pulse Connect Secure](../connectors/pulseconnectsecure.md) |

[← Back to Solutions Index](../solutions-index.md)
