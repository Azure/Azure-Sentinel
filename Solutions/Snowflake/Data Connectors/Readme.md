# Integrating Snowflake into Microsoft Sentinel
## Table Of Contents
- [Introduction](#intro)
- [Steps to obtain the Snowflake Account Identifier](#accountId)
- [Authentication requirements](#authentication)
- [Configure Snowflake OAuth](#snowflake-oauth)
- [Update or troubleshoot an OAuth connection](#oauth-maintenance)
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

<a name = "authentication">

## Authentication requirements

The Snowflake 3.2.3 Codeless Connector Framework (CCF) connector uses Snowflake OAuth with a confidential custom-client integration for all ten V3 log types. PAT and External OAuth authentication are not offered by this release. These settings do not change the legacy Azure Function connector.

Use the account hostname prefix as the **Snowflake Account Identifier**, for example `exampleorg-prod` for `https://exampleorg-prod.snowflakecomputing.com`. Do not include `https://`, `.snowflakecomputing.com`, or a URL path in this field.

Before connecting:

- Configure a least-privilege Snowflake role that can read the selected `SNOWFLAKE.ACCOUNT_USAGE` views. Some views require different Snowflake database roles; confirm access to every selected view.
- Ensure that the mapped user has an accessible default warehouse and the necessary warehouse usage privileges. The connector does not set a role or warehouse in its SQL requests.
- Allow the connector's outbound traffic through your existing Snowflake network policy. OAuth does not require opening the account to all IP addresses.
- Enter secrets only in the connector's password fields. Never put secrets, authorization codes, or tokens in source files or support requests.

<a name = "snowflake-oauth">

## Configure Snowflake OAuth

This option uses Snowflake as the authorization server, with the `authorization_code` grant and `refresh_token` scope. It is not the External OAuth client credentials flow.

1. Have an authorized Snowflake administrator create a confidential custom OAuth integration. For example:

   ```sql
   CREATE SECURITY INTEGRATION SENTINEL_OAUTH
     TYPE = OAUTH
     ENABLED = TRUE
     OAUTH_CLIENT = CUSTOM
     OAUTH_CLIENT_TYPE = 'CONFIDENTIAL'
     OAUTH_REDIRECT_URI = 'https://ms.portal.azure.com/TokenAuthorize/ExtensionName/Microsoft_Azure_Security_Insights'
     OAUTH_ISSUE_REFRESH_TOKENS = TRUE;
   ```

   For an existing integration, register the same callback using `OAUTH_REDIRECT_URI` or `OAUTH_ALTERNATE_REDIRECT_URIS`. The callback must match exactly, including its hostname and path. This connector is configured only for the `ms.portal.azure.com` callback; callbacks for other Azure or Defender portal hosts are not interchangeable.

2. Obtain the integration's client ID and client secret securely:

   ```sql
   SELECT SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('SENTINEL_OAUTH');
   ```

3. Configure the consenting user's default role and warehouse to meet the prerequisites above. The requested scope does not specify a role, so Snowflake uses the user's default role. Do not use `ACCOUNTADMIN` or `SECURITYADMIN` as the connector's runtime role.
4. In Microsoft Sentinel, open the Snowflake CCF connector and select **Add Account**. Enter a unique connection alias, select the log types, and enter the account identifier.
5. Enter the full authorization URL for that same account, for example `https://<account-identifier>.snowflakecomputing.com/oauth/authorize`. Enter a literal HTTPS URL, not an ARM expression or a `{{accountId}}` placeholder.
6. Enter the integration's client ID and client secret, then connect and complete the Snowflake sign-in and consent flow.

The token endpoint is derived from the account identifier as `https://<accountId>.snowflakecomputing.com/oauth/token-request`. Token requests use form encoding and HTTP Basic client authentication. SQL API requests use a bearer token with `X-Snowflake-Authorization-Token-Type: OAUTH`.

Refresh tokens have a finite lifetime; enabling them does not create permanent access. Monitor token expiry, revoked consent, and secret rotation. Integrations that require additional grant mechanisms such as PKCE or private-key JWT are not configured by this client-secret connector.

See [Configure Snowflake OAuth for custom clients](https://docs.snowflake.com/en/user-guide/oauth-custom) for integration settings, refresh-token policies, and role restrictions.

<a name = "oauth-maintenance">

## Update or troubleshoot an OAuth connection

- To update an OAuth connection, use the same connection alias and reauthorize with the integration's current credentials.
- When migrating from PAT, record the existing connection alias and selected log types, delete the existing connection rows for that alias, then reconnect using Snowflake OAuth. Verify the replacement connection before leaving it unattended; avoid running duplicate connections for the same log types.
- For a redirect mismatch, compare the integration's registered URI with the exact callback above and confirm that the authorization URL and account identifier refer to the same Snowflake account.
- For Snowflake OAuth refresh failures, check refresh-token lifetime, revoked consent, client-secret validity, and integration policy, then reauthorize.
 
- If authentication succeeds but queries fail, check warehouse access and privileges for every selected `ACCOUNT_USAGE` view. Do not broaden network or role permissions just to suppress an error.
- The connector retains the existing 120-minute query delay for `ACCOUNT_USAGE` latency. A successful connection does not imply immediate log arrival.

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
