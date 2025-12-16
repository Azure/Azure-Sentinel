# Microsoft Project

| | |
|----------|-------|
| **Connector ID** | `Office365Project` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ProjectActivity`](../tables-index.md#projectactivity) |
| **Used in Solutions** | [Microsoft Project](../solutions/microsoft-project.md) |
| **Connector Definition Files** | [template_Office365Project.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Project/Data%20Connectors/template_Office365Project.JSON) |

Microsoft Project (MSP) is a project management software solution. Depending on your plan, Microsoft Project lets you plan projects, assign tasks, manage resources, create reports and more. This connector allows you to stream your Azure Project audit logs into Microsoft Sentinel in order to track your project activities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **License**: "Microsoft Project eligible license is required."

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Project audit logs to Microsoft Sentinel**

This connector uses the Office Management API to get your Project audit logs. The logs will be stored and processed in your existing Microsoft Sentinel workspace. You can find the data in the **ProjectActivity** table.
- Connect Microsoft Project

[← Back to Connectors Index](../connectors-index.md)
