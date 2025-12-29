# Snowflake

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

The Snowflake data connector provides the capability to ingest Snowflake [login logs](https://docs.snowflake.com/en/sql-reference/account-usage/login_history.html) and [query logs](https://docs.snowflake.com/en/sql-reference/account-usage/query_history.html) into Microsoft Sentinel using the Snowflake Python Connector. Refer to [Snowflake  documentation](https://docs.snowflake.com/en/user-guide/python-connector.html) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Snowflake_CL` |
| **Connector Definition Files** | [Snowflake_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake/Data%20Connectors/Snowflake_API_FunctionApp.json) |

[→ View full connector details](../connectors/snowflakedataconnector.md)

### [Snowflake (via Codeless Connector Framework)](../connectors/snowflakelogsccpdefinition.md)

**Publisher:** Microsoft

The Snowflake data connector provides the capability to ingest Snowflake [Login History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/login_history), [Query History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/query_history), [User-Grant Logs](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_users), [Role-Grant Logs](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles), [Load History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/load_history), [Materialized View Refresh History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/materialized_view_refresh_history), [Roles Logs](https://docs.snowflake.com/en/sql-reference/account-usage/roles), [Tables Logs](https://docs.snowflake.com/en/sql-reference/account-usage/tables), [Table Storage Metrics Logs](https://docs.snowflake.com/en/sql-reference/account-usage/table_storage_metrics), [Users Logs](https://docs.snowflake.com/en/sql-reference/account-usage/users) into Microsoft Sentinel using the Snowflake SQL API. Refer to [Snowflake SQL API documentation](https://docs.snowflake.com/en/developer-guide/sql-api/reference) for more information.

| Attribute | Value |
|:-------------------------|:---|
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

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.8       | 22-12-2025                     | Added a 120‑minute ingestion delay for the **Snowflake connector** and updated the parser KQL to surface accurate start/end timestamps.|
| 3.0.7       | 10-12-2025                     | Resolved bug in **CCF Data Connector** related to Output stream for Snowflake tables.    |
| 3.0.6       | 20-11-2025                     | Resolved bug in **CCF Data Connector** related to SQL queries      |
| 3.0.5       | 13-10-2025                     | Updated Parser to support function app table                       |
| 3.0.4       | 23-09-2025                     | Updated parser to extend the normalized fields, and updated Analytic Rules, Workbooks to use CCF connector fields.                              |
| 3.0.3       | 09-09-2025                     | Updated DCR and Poller to prevent redundant data ingestion, improve pagination and handle connection interruptions for **Snowflake CCF connector**|
| 3.0.2       | 20-08-2025                     | Moving Snowflake **CCF Data Connector** to GA.|
| 3.0.1       | 26-05-2025                     | Migrated the **Function app** connector to **CCP** Data Connector and Updated **Parser**|
| 3.0.0       | 31-08-2023                     | Manual deployment instructions updated for **Data Connector** & Convert **Parser** from text to Yaml|

[← Back to Solutions Index](../solutions-index.md)
