# [DEPRECATED] Snowflake

| | |
|----------|-------|
| **Connector ID** | `SnowflakeDataConnector` |
| **Publisher** | Snowflake |
| **Tables Ingested** | [`Snowflake_CL`](../tables-index.md#snowflake_cl) |
| **Used in Solutions** | [Snowflake](../solutions/snowflake.md) |
| **Connector Definition Files** | [Snowflake_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Snowflake/Data%20Connectors/Snowflake_API_FunctionApp.json) |

The Snowflake data connector provides the capability to ingest Snowflake [login logs](https://docs.snowflake.com/en/sql-reference/account-usage/login_history.html) and [query logs](https://docs.snowflake.com/en/sql-reference/account-usage/query_history.html) into Microsoft Sentinel using the Snowflake Python Connector. Refer to [Snowflake  documentation](https://docs.snowflake.com/en/user-guide/python-connector.html) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
