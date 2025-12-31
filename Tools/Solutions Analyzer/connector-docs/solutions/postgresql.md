# PostgreSQL

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PostgreSQL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PostgreSQL) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] PostgreSQL Events](../connectors/postgresql.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`PostgreSQL_CL`](../tables/postgresql-cl.md) | [[Deprecated] PostgreSQL Events](../connectors/postgresql.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [PostgreSQLEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PostgreSQL/Parsers/PostgreSQLEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------|
| 3.0.1       | 12-12-2024                     | Removed Deprecated **Data connectors**                                       |
| 3.0.0       | 09-08-2024                     | Deprecating data connectors                                                  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
