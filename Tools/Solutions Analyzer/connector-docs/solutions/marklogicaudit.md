# MarkLogicAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-08-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MarkLogicAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MarkLogicAudit) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] MarkLogic Audit](../connectors/marklogic.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`MarkLogicAudit_CL`](../tables/marklogicaudit-cl.md) | [[Deprecated] MarkLogic Audit](../connectors/marklogic.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [MarkLogicAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MarkLogicAudit/Parsers/MarkLogicAudit.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                          |
|-------------|--------------------------------|-------------------------------------------------------------|
| 3.0.1       | 02-01-2025                     | Removed Deprecated **Data connector**                       |
| 3.0.0       | 12-08-2024                     | Deprecating data connector                                  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
