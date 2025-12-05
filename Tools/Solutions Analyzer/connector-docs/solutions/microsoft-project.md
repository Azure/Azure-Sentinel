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
