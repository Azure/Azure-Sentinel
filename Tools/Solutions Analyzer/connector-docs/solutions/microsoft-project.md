# Microsoft Project

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Project](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Project) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Project](../connectors/office365project.md)

**Publisher:** Microsoft

Microsoft Project (MSP) is a project management software solution. Depending on your plan, Microsoft Project lets you plan projects, assign tasks, manage resources, create reports and more. This connector allows you to stream your Azure Project audit logs into Microsoft Sentinel in order to track your project activities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **License**: "Microsoft Project eligible license is required."

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Project audit logs to Microsoft Sentinel**

This connector uses the Office Management API to get your Project audit logs. The logs will be stored and processed in your existing Microsoft Sentinel workspace. You can find the data in the **ProjectActivity** table.
- Connect Microsoft Project

| | |
|--------------------------|---|
| **Tables Ingested** | `ProjectActivity` |
| **Connector Definition Files** | [template_Office365Project.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Project/Data%20Connectors/template_Office365Project.JSON) |

[→ View full connector details](../connectors/office365project.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ProjectActivity` | [Microsoft Project](../connectors/office365project.md) |

[← Back to Solutions Index](../solutions-index.md)
