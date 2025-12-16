# OneTrust

| | |
|----------|-------|
| **Connector ID** | `OnetrustPush` |
| **Publisher** | OneTrust |
| **Tables Ingested** | [`OneTrustMetadataV3_CL`](../tables-index.md#onetrustmetadatav3_cl) |
| **Used in Solutions** | [OneTrust](../solutions/onetrust.md) |
| **Connector Definition Files** | [OneTrustLogs_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneTrust/Data%20Connectors/OneTrustLogs_CCF/OneTrustLogs_connectorDefinition.json) |

The OneTrust connector for Microsoft Sentinel provides the capability to have near real time visibility into where sensitive data has been located or remediated across across Google Cloud and other OneTrust supported data sources.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Microsoft Entra**: Permission to create an app registration in Microsoft Entra ID. Typically requires Entra ID Application Developer role or higher.
- **Microsoft Azure**: Permission to assign Monitoring Metrics Publisher role on data collection rule (DCR). Typically requires Azure RBAC Owner or User Access Administrator role

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Create ARM Resources and Provide the Required Permissions**

This connector reads data from the tables that OneTrust uses in a Microsoft Analytics Workspace. If OneTrust's data forwarding option is enabled then raw event data can be sent to the Microsoft Sentinel Ingestion API.
#### Automated Configuration and Secure Data Ingestion with Entra Application 
Clicking on "Deploy" will trigger the creation of Log Analytics tables and a Data Collection Rule (DCR). 
It will then create an Entra application, link the DCR to it, and set the entered secret in the application. This setup enables data to be sent securely to the DCR using an Entra token.
Deploy OneTrust connector resources

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
- **OneTrust Metadata Stream Name**: `Custom-OneTrustMetadataV3`

[← Back to Connectors Index](../connectors-index.md)
