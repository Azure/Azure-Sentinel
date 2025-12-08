# Windows Security Events

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Security Events via Legacy Agent](../connectors/securityevents.md)

**Publisher:** Microsoft

### [Windows Security Events via AMA](../connectors/windowssecurityevents.md)

**Publisher:** Microsoft

You can stream all security events from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220225&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `SecurityEvent` |
| **Connector Definition Files** | [template_WindowsSecurityEvents.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Data%20Connectors/template_WindowsSecurityEvents.JSON) |

[→ View full connector details](../connectors/windowssecurityevents.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityEvent` | [Security Events via Legacy Agent](../connectors/securityevents.md), [Windows Security Events via AMA](../connectors/windowssecurityevents.md) |

[← Back to Solutions Index](../solutions-index.md)
