# Snowflake (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `SnowflakeLogsCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SnowflakeLoad_CL`](../tables-index.md#snowflakeload_cl), [`SnowflakeLogin_CL`](../tables-index.md#snowflakelogin_cl), [`SnowflakeMaterializedView_CL`](../tables-index.md#snowflakematerializedview_cl), [`SnowflakeQuery_CL`](../tables-index.md#snowflakequery_cl), [`SnowflakeRoleGrant_CL`](../tables-index.md#snowflakerolegrant_cl), [`SnowflakeRoles_CL`](../tables-index.md#snowflakeroles_cl), [`SnowflakeTableStorageMetrics_CL`](../tables-index.md#snowflaketablestoragemetrics_cl), [`SnowflakeTables_CL`](../tables-index.md#snowflaketables_cl), [`SnowflakeUserGrant_CL`](../tables-index.md#snowflakeusergrant_cl), [`SnowflakeUsers_CL`](../tables-index.md#snowflakeusers_cl) |
| **Used in Solutions** | [Snowflake](../solutions/snowflake.md) |
| **Connector Definition Files** | [SnowflakeLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake/Data%20Connectors/SnowflakeLogs_ccp/SnowflakeLogs_ConnectorDefinition.json) |

The Snowflake data connector provides the capability to ingest Snowflake [Login History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/login_history), [Query History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/query_history), [User-Grant Logs](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_users), [Role-Grant Logs](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles), [Load History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/load_history), [Materialized View Refresh History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/materialized_view_refresh_history), [Roles Logs](https://docs.snowflake.com/en/sql-reference/account-usage/roles), [Tables Logs](https://docs.snowflake.com/en/sql-reference/account-usage/tables), [Table Storage Metrics Logs](https://docs.snowflake.com/en/sql-reference/account-usage/table_storage_metrics), [Users Logs](https://docs.snowflake.com/en/sql-reference/account-usage/users) into Microsoft Sentinel using the Snowflake SQL API. Refer to [Snowflake SQL API documentation](https://docs.snowflake.com/en/developer-guide/sql-api/reference) for more information.

[← Back to Connectors Index](../connectors-index.md)
