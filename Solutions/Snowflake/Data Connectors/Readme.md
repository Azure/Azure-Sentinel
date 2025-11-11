# Integrating Snowflake into Microsoft Sentinel
## Table Of Contents
- [Introduction](#intro)
- [Steps to obtain the Snowflake Account Identifier](#accountId)
- [Steps to obtain Programmatic Access Token in Snowflake](#pat)

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
- Execute the following SQL statements to create and apply a permissive network policy:
  ```
  CREATE OR REPLACE NETWORK POLICY allow_all_ips
    ALLOWED_IP_LIST = ('0.0.0.0/0');
  ```
  ```
  ALTER ACCOUNT SET NETWORK_POLICY = allow_all_ips;
  ```
Once these commands are successfully executed, the network policy configuration is complete.
### Generate Programmatic Access Token
--------------------------------------------------------------------------------------------

- In the left context pane, click on your **Profile**.
- Click on **Settings**.
- Under the **Programmatic access tokens** section, click **Generate new token**.
- Copy and securely store the generated token, as it will only be displayed once.