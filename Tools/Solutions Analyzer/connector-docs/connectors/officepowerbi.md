# Microsoft PowerBI

| | |
|----------|-------|
| **Connector ID** | `OfficePowerBI` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`PowerBIActivity`](../tables-index.md#powerbiactivity) |
| **Used in Solutions** | [Microsoft PowerBI](../solutions/microsoft-powerbi.md) |
| **Connector Definition Files** | [template_OfficePowerBI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20PowerBI/Data%20Connectors/template_OfficePowerBI.json) |

Microsoft PowerBI is a collection of software services, apps, and connectors that work together to turn your unrelated sources of data into coherent, visually immersive, and interactive insights. Your data may be an Excel spreadsheet, a collection of cloud-based and on-premises hybrid data warehouses, or a data store of some other type. This connector lets you stream PowerBI audit logs into Microsoft Sentinel, allowing you to track user activities in your PowerBI environment. You can filter the audit data by date range, user, dashboard, report, dataset, and activity type.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **License**: Microsoft Power BI eligible license is required.

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft PowerBI audit logs to Microsoft Sentinel**

This connector uses the Office Management API to get your PowerBI audit logs. The logs will be stored and processed in your existing Microsoft Sentinel workspace. You can find the data in the **PowerBIActivity** table.
- Connect Microsoft PowerBI

[← Back to Connectors Index](../connectors-index.md)
