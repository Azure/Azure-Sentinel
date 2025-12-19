# Cisco ASA/FTD via AMA

| | |
|----------|-------|
| **Connector ID** | `CiscoAsaAma` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [CiscoASA](../solutions/ciscoasa.md) |
| **Connector Definition Files** | [template_CiscoAsaAma.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA/Data%20Connectors/template_CiscoAsaAma.JSON) |

The Cisco ASA firewall connector allows you to easily connect your Cisco ASA logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace data sources** (Workspace): read and write permissions.

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Enable data collection rule​**

> Cisco ASA/FTD event logs are collected only from **Linux** agents.
- Configure CiscoAsaAma data connector

- **Create data collection rule**

**2. Run the following command to install and apply the Cisco ASA/FTD collector:**

[← Back to Connectors Index](../connectors-index.md)
