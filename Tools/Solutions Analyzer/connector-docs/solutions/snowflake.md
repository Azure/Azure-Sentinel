# Snowflake

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [DEPRECATED] Snowflake

**Publisher:** Snowflake

The Snowflake data connector provides the capability to ingest Snowflake [login logs](https://docs.snowflake.com/en/sql-reference/account-usage/login_history.html) and [query logs](https://docs.snowflake.com/en/sql-reference/account-usage/query_history.html) into Microsoft Sentinel using the Snowflake Python Connector. Refer to [Snowflake  documentation](https://docs.snowflake.com/en/user-guide/python-connector.html) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

**Tables Ingested:**

- `Snowflake_CL`

**Connector Definition Files:**

- [Snowflake_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake/Data%20Connectors/Snowflake_API_FunctionApp.json)

### Snowflake (via Codeless Connector Framework)

**Publisher:** Microsoft

The Snowflake data connector provides the capability to ingest Snowflake [Login History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/login_history), [Query History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/query_history), [User-Grant Logs](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_users), [Role-Grant Logs](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles), [Load History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/load_history), [Materialized View Refresh History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/materialized_view_refresh_history), [Roles Logs](https://docs.snowflake.com/en/sql-reference/account-usage/roles), [Tables Logs](https://docs.snowflake.com/en/sql-reference/account-usage/tables), [Table Storage Metrics Logs](https://docs.snowflake.com/en/sql-reference/account-usage/table_storage_metrics), [Users Logs](https://docs.snowflake.com/en/sql-reference/account-usage/users) into Microsoft Sentinel using the Snowflake SQL API. Refer to [Snowflake SQL API documentation](https://docs.snowflake.com/en/developer-guide/sql-api/reference) for more information.

**Tables Ingested:**

- `SnowflakeLoad_CL`
- `SnowflakeLogin_CL`
- `SnowflakeMaterializedView_CL`
- `SnowflakeQuery_CL`
- `SnowflakeRoleGrant_CL`
- `SnowflakeRoles_CL`
- `SnowflakeTableStorageMetrics_CL`
- `SnowflakeTables_CL`
- `SnowflakeUserGrant_CL`
- `SnowflakeUsers_CL`

**Connector Definition Files:**

- [SnowflakeLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake/Data%20Connectors/SnowflakeLogs_ccp/SnowflakeLogs_ConnectorDefinition.json)

## Tables Reference

This solution ingests data into **11 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SnowflakeLoad_CL` | Snowflake (via Codeless Connector Framework) |
| `SnowflakeLogin_CL` | Snowflake (via Codeless Connector Framework) |
| `SnowflakeMaterializedView_CL` | Snowflake (via Codeless Connector Framework) |
| `SnowflakeQuery_CL` | Snowflake (via Codeless Connector Framework) |
| `SnowflakeRoleGrant_CL` | Snowflake (via Codeless Connector Framework) |
| `SnowflakeRoles_CL` | Snowflake (via Codeless Connector Framework) |
| `SnowflakeTableStorageMetrics_CL` | Snowflake (via Codeless Connector Framework) |
| `SnowflakeTables_CL` | Snowflake (via Codeless Connector Framework) |
| `SnowflakeUserGrant_CL` | Snowflake (via Codeless Connector Framework) |
| `SnowflakeUsers_CL` | Snowflake (via Codeless Connector Framework) |
| `Snowflake_CL` | [DEPRECATED] Snowflake |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n