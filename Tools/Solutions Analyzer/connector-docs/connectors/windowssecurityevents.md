# Windows Security Events via AMA

| | |
|----------|-------|
| **Connector ID** | `WindowsSecurityEvents` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SecurityEvent`](../tables-index.md#securityevent) |
| **Used in Solutions** | [Windows Security Events](../solutions/windows-security-events.md) |
| **Connector Definition Files** | [template_WindowsSecurityEvents.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Data%20Connectors/template_WindowsSecurityEvents.JSON) |

You can stream all security events from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220225&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace data sources** (Workspace): read and write permissions.

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Enable data collection rule​**

>  Security Events logs are collected only from **Windows** agents.
- Configure WindowsSecurityEvents data connector

- **Create data collection rule**

[← Back to Connectors Index](../connectors-index.md)
