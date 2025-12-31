# MongoDBAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAudit) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] MongoDB Audit](../connectors/mongodb.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`MongoDBAudit_CL`](../tables/mongodbaudit-cl.md) | [[Deprecated] MongoDB Audit](../connectors/mongodb.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [MongoDBAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MongoDBAudit/Parsers/MongoDBAudit.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 23-12-2024                     | Removed Deprecated **Data connector**       |
| 3.0.0       |  08-08-2024                    | Deprecating data connectors                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
