# Fortinet FortiGate Next-Generation Firewall connector for Microsoft Sentinel

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-08-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Fortinet via Legacy Agent](../connectors/fortinet.md)

**Publisher:** Fortinet

### [[Deprecated] Fortinet via AMA](../connectors/fortinetama.md)

**Publisher:** Fortinet

The Fortinet firewall connector allows you to easily connect your Fortinet logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_Fortinet-FortiGateAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/template_Fortinet-FortiGateAma.json) |

[→ View full connector details](../connectors/fortinetama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Fortinet via AMA](../connectors/fortinetama.md), [[Deprecated] Fortinet via Legacy Agent](../connectors/fortinet.md) |

[← Back to Solutions Index](../solutions-index.md)
