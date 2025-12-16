# Microsoft 365

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft 365 (formerly, Office 365)](../connectors/office365.md)

**Publisher:** Microsoft

The Microsoft 365 (formerly, Office 365) activity log connector provides insight into ongoing user activities. You will get details of operations such as file downloads, access requests sent, changes to group events, set-mailbox and details of the user who performed the actions. By connecting Microsoft 365 logs into Microsoft Sentinel you can use this data to view dashboards, create custom alerts, and improve your investigation process. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2219943&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Office 365 activity logs to your Microsoft Sentinel.**

Select the record types you want to collect from your tenant and click **Apply Changes**.
**Select Microsoft 365 Data Types**

In the Microsoft Sentinel portal, select which data types to enable:

- ☐ **Exchange**
- ☐ **SharePoint**
- ☐ **Teams**

Each data type may have specific licensing requirements. Review the information provided for each type in the portal before enabling.

> 💡 **Portal-Only Feature**: Data type selection is only available in the Microsoft Sentinel portal.


**2. Previously connected tenants**

Microsoft Sentinel now enables Office 365 single-tenant connection. You can modify your previously connected tenants and click **Save**.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `Office365`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

| | |
|--------------------------|---|
| **Tables Ingested** | `OfficeActivity` |
| | `exchange` |
| | `sharePoint` |
| | `teams` |
| **Connector Definition Files** | [Microsoft365.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Data%20Connectors/Microsoft365.JSON) |

[→ View full connector details](../connectors/office365.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OfficeActivity` | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) |
| `exchange` | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) |
| `sharePoint` | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) |
| `teams` | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) |

[← Back to Solutions Index](../solutions-index.md)
