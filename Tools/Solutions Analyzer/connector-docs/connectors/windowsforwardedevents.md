# Windows Forwarded Events

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `WindowsForwardedEvents` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [Windows Forwarded Events](../solutions/windows-forwarded-events.md) |
| **Collection Method** | AMA |
| **Connector Definition Files** | [WindowsForwardedEvents.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events/Data%20Connectors/WindowsForwardedEvents.JSON) |

You can stream all Windows Event Forwarding (WEF) logs from the Windows Servers connected to your Microsoft Sentinel workspace using Azure Monitor Agent (AMA).

	This connection enables you to view dashboards, create custom alerts, and improve investigation.

	This gives you more insight into your organization’s network and improves your security operation capabilities. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2219963&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`WindowsEvent`](../tables/windowsevent.md) | ✓ | ✓ |

> 💡 **Tip:** Tables with Ingestion API support allow data ingestion via the [Azure Monitor Data Collector API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview), which also enables custom transformations during ingestion.

## Permissions

**Resource Provider Permissions:**
- **Workspace data sources** (Workspace): read and write permissions.

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Enable data collection rule​**

>  Windows Forwarded Events logs are collected only from **Windows** agents.
- Configure WindowsForwardedEvents data connector
- **Create data collection rule**
- **Install/configure: OpenCustomDeploymentBlade**

[← Back to Connectors Index](../connectors-index.md)
