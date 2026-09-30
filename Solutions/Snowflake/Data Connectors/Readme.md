# Integrating Snowflake into Microsoft Sentinel
## Table Of Contents
- [Introduction](#intro)
- [Steps to obtain the Snowflake Account Identifier](#accountId)
- [Steps to obtain Programmatic Access Token in Snowflake](#pat)
- [Understand V3 row-level ingestion](#v3-ingestion)

<a name = "intro">

## Introduction
The Snowflake Codeless Connector for Microsoft Sentinel enables seamless integration of Snowflake's Login History, Query History, User-Grant, Role-Grant, Load History, Materialized View Refresh History, Roles, Tables, Table Storage Metrics, Users Logs with Microsoft Sentinel without the need for custom code.

<a name = "accountId">
  
## Steps to obtain the Snowflake Account Identifier
- Log in to your Snowflake account using your username and password.
- In the left context pane, click on your **Profile name**.
- Hover over the **Account** section to reveal additional options.
- Click on **View account details**.
- Locate and copy the **Account Identifier** for future reference or configuration needs.

<a name = "pat">
  
## Steps to obtain Programmatic Access Token in Snowflake
To enable permanent access via a Programmatic Access Token, configuring a **Network Policy** is a mandatory prerequisite. Follow the steps below to configure the network policy and generate the token.
### Configure Network Policy

--------------------------------------------------------------------------------------------------------------------

- Log in to your Snowflake account and navigate to a **SQL Worksheet**.
- Execute **only one** of the following configurations based on your specific scenario:
  #### Scenario 1: No Existing IP Restrictions
  - If there are no prior IP restrictions, create and apply a permissive network policy that allows access from all IP addresses:
    ```
    CREATE OR REPLACE NETWORK POLICY allow_all_ips
      ALLOWED_IP_LIST = ('0.0.0.0/0');
    ```
    ```
    ALTER ACCOUNT SET NETWORK_POLICY = allow_all_ips;
    ```
  #### Scenario 2: Existing IP Restrictions
  - If your account already has IP restrictions in place, you can create a more flexible policy that allows all IPs but explicitly blocks specific addresses:
    ```
    CREATE OR REPLACE NETWORK POLICY allow_all_with_blocks
      ALLOWED_IP_LIST = ('0.0.0.0/0')
      BLOCKED_IP_LIST = ('<IP_ADDRESS1>', '<IP_ADDRESS2>');
    ```
    ```
    ALTER ACCOUNT SET NETWORK_POLICY = allow_all_with_blocks;
    ```
    > **Note:** If you have multiple blocked IP addresses, provide all IP addresses separated by commas as shown in above query.

Once these commands are successfully executed, the network policy configuration is complete.
### Generate Programmatic Access Token
--------------------------------------------------------------------------------------------

- In the left context pane, click on your **Profile**.
- Click on **Settings**.
- Under the **Programmatic access tokens** section, click **Generate new token**.
- Copy and securely store the generated token, as it will only be displayed once.
<a name = "v3-ingestion">

## Understand V3 row-level ingestion

The Snowflake SQL API returns query results in a `data` array. Each array element represents one Snowflake record. The values are positional, and the response does not include source column names.

For example:

```json
{
  "data": [
    ["1001", "2026-09-22 10:00:00.000 +0000", "LOGIN", "USER_A"],
    ["1002", "2026-09-22 10:01:00.000 +0000", "LOGIN", "USER_B"]
  ]
}
```

### Why V3 was introduced

Earlier connector versions stored the result array in a generic `Data` column. At query time, the parser used `mv-expand` to expand the multivalue array and extract values into named fields. 
V3 instead ingests each Snowflake record as a separate Log Analytics row with named columns. This design makes fields available for direct query and removes query-time array expansion for V3 data.

### How the connector processes V3 data

The connector processes the response as follows:

1. The connector uses the `$.data` JSONPath expression to select the Snowflake result array.
1. The SCUBA processing service applies `/ASI/Microsoft/MvExpandTransformer` to expand the array into individual records.
1. The transformer exposes the values in each positional record as `col0`, `col1`, `col2`, through `colN`.
1. The data collection rule (DCR) maps each positional field to the corresponding Snowflake column name.
1. The DCR writes the named fields to the appropriate `Snowflake*V3_CL` table.

For example, the transformer presents an expanded Login History record to the DCR in the following form:

```text
col0 = "1001"
col1 = "2026-09-22 10:00:00.000 +0000"
col2 = "LOGIN"
col3 = "USER_A"
```

The DCR converts the positional fields into named columns:

```kusto
source
| project
    TimeGenerated = now(),
    SnowflakeAccountIdentifier = tostring(accountId),
    EventId = tostring(col0),
    EventTimestamp = tostring(col1),
    EventType = tostring(col2),
    UserName = tostring(col3)
```

The resulting Log Analytics record contains named fields such as `EventId`, `EventTimestamp`, `EventType`, and `UserName`.

> [!IMPORTANT]
> The positional order is part of the ingestion contract. When you add, remove, or reorder a column in a Snowflake `SELECT` statement, update all related components.

Keep the following components aligned:

- The column order in the Snowflake SQL statement.
- The DCR stream declaration from `col0` through `colN`.
- The index-to-name mapping in `transformKql`.
- The destination V3 table schema.
- The V3 parser mapping.
