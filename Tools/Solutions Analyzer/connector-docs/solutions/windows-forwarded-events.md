# Windows Forwarded Events

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Windows Forwarded Events](../connectors/windowsforwardedevents.md)

**Publisher:** Microsoft

You can stream all Windows Event Forwarding (WEF) logs from the Windows Servers connected to your Microsoft Sentinel workspace using Azure Monitor Agent (AMA).

	This connection enables you to view dashboards, create custom alerts, and improve investigation.

	This gives you more insight into your organization’s network and improves your security operation capabilities. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2219963&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `WindowsEvent` |
| **Connector Definition Files** | [WindowsForwardedEvents.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events/Data%20Connectors/WindowsForwardedEvents.JSON) |

[→ View full connector details](../connectors/windowsforwardedevents.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `WindowsEvent` | [Windows Forwarded Events](../connectors/windowsforwardedevents.md) |

[← Back to Solutions Index](../solutions-index.md)
