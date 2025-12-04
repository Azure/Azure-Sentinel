# Infoblox NIOS

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-04-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Infoblox NIOS](../connectors/infobloxnios.md)

**Publisher:** Infoblox

The [Infoblox Network Identity Operating System (NIOS)](https://www.infoblox.com/glossary/network-identity-operating-system-nios/) connector allows you to easily connect your Infoblox NIOS logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_Infoblox.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20NIOS/Data%20Connectors/Connector_Syslog_Infoblox.json) |

[→ View full connector details](../connectors/infobloxnios.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Infoblox NIOS](../connectors/infobloxnios.md) |

[← Back to Solutions Index](../solutions-index.md)
