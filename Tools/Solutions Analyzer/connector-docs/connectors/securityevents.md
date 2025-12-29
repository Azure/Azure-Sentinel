# Security Events via Legacy Agent

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `SecurityEvents` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [Windows Security Events](../solutions/windows-security-events.md) |
| **Collection Method** | MMA |
| **Connector Definition Files** | [template_SecurityEvents.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Data%20Connectors/template_SecurityEvents.JSON) |

You can stream all security events from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220093&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`SecurityEvent`](../tables/securityevent.md) | — | ✓ |

> 💡 **Tip:** Tables with Ingestion API support allow data ingestion via the [Azure Monitor Data Collector API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview), which also enables custom transformations during ingestion.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Workspace data sources** (Workspace): read and write permissions.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Download and install the agent**

>  Security Events logs are collected only from **Windows** agents.
**Choose where to install the agent:**

**Install agent on Azure Windows Virtual Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install/configure: InstallAgentOnVirtualMachine**

  **Install agent on non-Azure Windows Machine**

  Select the machine to install the agent and then click **Connect**.
  - **Install/configure: InstallAgentOnNonAzure**

**2. Select which events to stream**

- All events - All Windows security and AppLocker events.
- Common - A standard set of events for auditing purposes.
- Minimal - A small set of events that might indicate potential threats. By enabling this option, you won't be able to have a full audit trail.
- None - No security or AppLocker events.
- Configure SecurityEvents data connector

[← Back to Connectors Index](../connectors-index.md)
