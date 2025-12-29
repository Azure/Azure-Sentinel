# Microsoft 365 Assets

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-06-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365%20Assets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365%20Assets) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft 365 Assets (formerly, Office 365)](../connectors/m365assets.md)

**Publisher:** Microsoft

The Microsoft 365 (formerly, Office 365) asset connector gives richer insights into ongoing user activities in Microsoft Sentinel by supplementing activity logs with details such as owners, permissions, retention policies and sensitivity labels.



Data from this connector is used to build data risk graphs in Purview. If you've enabled those graphs, deactivating this connector will prevent the graphs from being built. [Learn about the data risk graph](https://go.microsoft.com/fwlink/?linkid=2320023).



This connector is in limited private preview.

**Permissions:**

**Custom Permissions:**
- **OfficeActivity table availability**: Enable the OfficeActivity table in Log Analytics.

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

1.Connect Microsoft 365 assets (formerly, Office 365) to Microsoft Sentinel.
  - SharePoint and OneDrive

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `` |
| **Connector Definition Files** | [M365Asset_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365%20Assets/Data%20Connectors/M365Asset_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/m365assets.md)

[← Back to Solutions Index](../solutions-index.md)
