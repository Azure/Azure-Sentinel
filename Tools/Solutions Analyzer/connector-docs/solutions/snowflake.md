# Snowflake

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] Snowflake](../connectors/snowflakedataconnector.md)

**Publisher:** Snowflake

### [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md)

**Publisher:** Microsoft

The Snowflake data connector provides the capability to ingest Snowflake [Login History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/login_history), [Query History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/query_history), [User-Grant Logs](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_users), [Role-Grant Logs](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles), [Load History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/load_history), [Materialized View Refresh History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/materialized_view_refresh_history), [Roles Logs](https://docs.snowflake.com/en/sql-reference/account-usage/roles), [Tables Logs](https://docs.snowflake.com/en/sql-reference/account-usage/tables), [Table Storage Metrics Logs](https://docs.snowflake.com/en/sql-reference/account-usage/table_storage_metrics), [Users Logs](https://docs.snowflake.com/en/sql-reference/account-usage/users) into Microsoft Sentinel using the Snowflake SQL API. Refer to [Snowflake SQL API documentation](https://docs.snowflake.com/en/developer-guide/sql-api/reference) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `SnowflakeLoad_CL` |
| | `SnowflakeLogin_CL` |
| | `SnowflakeMaterializedView_CL` |
| | `SnowflakeQuery_CL` |
| | `SnowflakeRoleGrant_CL` |
| | `SnowflakeRoles_CL` |
| | `SnowflakeTableStorageMetrics_CL` |
| | `SnowflakeTables_CL` |
| | `SnowflakeUserGrant_CL` |
| | `SnowflakeUsers_CL` |
| **Connector Definition Files** | [SnowflakeLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake/Data%20Connectors/SnowflakeLogs_ccp/SnowflakeLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/snowflakelogsccpdefinition.md)

## Tables Reference

This solution ingests data into **11 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SnowflakeLoad_CL` | [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md) |
| `SnowflakeLogin_CL` | [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md) |
| `SnowflakeMaterializedView_CL` | [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md) |
| `SnowflakeQuery_CL` | [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md) |
| `SnowflakeRoleGrant_CL` | [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md) |
| `SnowflakeRoles_CL` | [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md) |
| `SnowflakeTableStorageMetrics_CL` | [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md) |
| `SnowflakeTables_CL` | [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md) |
| `SnowflakeUserGrant_CL` | [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md) |
| `SnowflakeUsers_CL` | [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md) |
| `Snowflake_CL` | [[DEPRECATED] Snowflake](../connectors/snowflakedataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
