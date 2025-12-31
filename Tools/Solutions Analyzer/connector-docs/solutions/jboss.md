# JBoss

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JBoss](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JBoss) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] JBoss Enterprise Application Platform](../connectors/jbosseap.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`JBossLogs_CL`](../tables/jbosslogs-cl.md) | [[Deprecated] JBoss Enterprise Application Platform](../connectors/jbosseap.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [JBossEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JBoss/Parsers/JBossEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                          |
|-------------|--------------------------------|-------------------------------------------------------------|
| 3.0.1       | 31-12-2024                     | Removed Deprecated **Data connector**                       |
| 3.0.0       | 13-08-2024                     | Deprecating data connector                                  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
