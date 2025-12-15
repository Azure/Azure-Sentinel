# Keeper Security Push Connector

| | |
|----------|-------|
| **Connector ID** | `KeeperSecurityPush2` |
| **Publisher** | Keeper Security |
| **Tables Ingested** | [`KeeperSecurityEventNewLogs_CL`](../tables-index.md#keepersecurityeventnewlogs_cl) |
| **Used in Solutions** | [Keeper Security](../solutions/keeper-security.md) |
| **Connector Definition Files** | [KepperSecurity_Definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security/Data%20Connectors/KeeperSecurity_ccp/KepperSecurity_Definition.json) |

The [Keeper Security](https://keepersecurity.com) connector provides the capability to read raw event data from Keeper Security in Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Microsoft Entra**: Permission to create an app registration in Microsoft Entra ID. Typically requires Entra ID Application Developer role or higher.
- **Microsoft Azure**: Permission to assign Monitoring Metrics Publisher role on data collection rule (DCR). Typically requires Azure RBAC Owner or User Access Administrator role

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Create ARM Resources and Provide the Required Permissions**

This connector reads data from the tables that Keeper Security uses in a Microsoft Analytics Workspace, if the [data forwarding](https://docs.keepersecurity.com/docs/data-forwarding) option is enabled in Keeper Security then raw event data is sent to the Microsoft Sentinel Ingestion API.
#### Automated Configuration and Secure Data Ingestion with Entra Application 
Clicking on "Deploy" will trigger the creation of Log Analytics tables and a Data Collection Rule (DCR). 
It will then create an Entra application, link the DCR to it, and set the entered secret in the application. This setup enables data to be sent securely to the DCR using an Entra token.
Keeper Security connector resources

**2. Push your logs into the workspace**

Use the following parameters to configure the your machine to send the logs to the workspace.
- **Tenant ID (Directory ID)**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra App Registration Application ID**: `ApplicationId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra App Registration Secret**: `ApplicationSecret`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Data Collection Endpoint Uri**: `DataCollectionEndpoint`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Data Collection Rule Immutable ID**: `DataCollectionRuleId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Events Logs Stream Name**: `Custom-KeeperSecurityEventNewLogs`

**3. Update Keeper Admin Console**

Configure the Keeper Admin Console with the Azure connection details to enable data forwarding to Microsoft Sentinel.
#### Configure Azure Monitor Logs in Keeper Admin Console

In the [Keeper Admin Console](https://keepersecurity.com/console/), login as the Keeper Administrator. Then go to **Reporting & Alerts** and select **Azure Monitor Logs**.

Provide the following information from Step 2 above into the Admin Console:

- **Azure Tenant ID**: You can find this from Azure's "Subscriptions" area.
- **Application (client) ID**: This is located in the App registration (KeeperLogging) overview screen
- **Client Secret Value**: This is the Client Secret Value from the app registration secrets.
- **Endpoint URL**: This is a URL that is created in the following specific format:
  `https://<collection_url>/dataCollectionRules/<dcr_id>/streams/<table>?api-version=2023-01-01`

To assemble the Endpoint URL:

- **<Collection URL>** This comes from Step 2 above
- **<DCR_ID>** From the Data Collector Rule, copy the "Immutable Id" value, e.g. `dcr-xxxxxxx`
- **<TABLE>** This is the table name created by Azure, e.g. `Custom-KeeperSecurityEventNewLogs`

Example: `https://<Collection_URL>/dataCollectionRules/<DCR_ID>/streams/Custom-KeeperSecurityEventNewLogs?api-version=2023-01-01`

[← Back to Connectors Index](../connectors-index.md)
