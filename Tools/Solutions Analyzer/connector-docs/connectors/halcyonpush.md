# Halcyon Connector

| | |
|----------|-------|
| **Connector ID** | `HalcyonPush` |
| **Publisher** | Halcyon |
| **Tables Ingested** | [`HalcyonAuthenticationEvents_CL`](../tables-index.md#halcyonauthenticationevents_cl), [`HalcyonDnsActivity_CL`](../tables-index.md#halcyondnsactivity_cl), [`HalcyonFileActivity_CL`](../tables-index.md#halcyonfileactivity_cl), [`HalcyonNetworkSession_CL`](../tables-index.md#halcyonnetworksession_cl), [`HalcyonProcessEvent_CL`](../tables-index.md#halcyonprocessevent_cl) |
| **Used in Solutions** | [Halcyon](../solutions/halcyon.md) |
| **Connector Definition Files** | [Halcyon_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Halcyon/Data%20Connectors/Halcyon_ccp/Halcyon_connectorDefinition.json) |

The [Halcyon](https://www.halcyon.ai) connector provides the capability to send data from Halcyon to Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace Permissions** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Microsoft Entra Create Permissions**: Permissions to create an app registration in Microsoft Entra ID. Typically requires Entra ID Application Developer role or higher.
- **Role Assignment Permissions**: Write permissions required to assign Monitoring Metrics Publisher role to the data collection rule (DCR). Typically requires Owner or User Access Administrator role at the resource group level.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Create ARM Resources and Provision Required Permissions**

This connector reads data from the tables that Halcyon uses in a Microsoft Analytics Workspace, if the data is being forwarded
#### Automated Configuration and Secure Data Ingestion with Entra Application 
Clicking on "Deploy" will trigger the creation of Log Analytics tables and a Data Collection Rule (DCR). 
It will then create an Entra application, link the DCR to it, and set the entered secret in the application. This setup enables data to be sent securely to the DCR using an Entra token.
Deploy Halcyon Connector Resources

**2. Configured your integration in the Halcyon Platform**

Use the following parameters to configure your integration in the Halcyon Platform.
- **Directory ID (Tenant ID)**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra App Registration Application ID (Client ID)**: `ApplicationId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra App Registration Secret (Credential Secret) (THIS SECRET WILL NOT BE VISIBLE AFTER LEAVING THIS PAGE)**: `ApplicationSecret`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Data Collection Endpoint (URL)**: `DataCollectionEndpoint`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Data Collection Rule Immutable ID (Rule ID)**: `DataCollectionRuleId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
