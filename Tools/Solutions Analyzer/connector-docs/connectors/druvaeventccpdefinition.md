# Druva Events Connector

| | |
|----------|-------|
| **Connector ID** | `DruvaEventCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`DruvaInsyncEvents_CL`](../tables-index.md#druvainsyncevents_cl), [`DruvaPlatformEvents_CL`](../tables-index.md#druvaplatformevents_cl), [`DruvaSecurityEvents_CL`](../tables-index.md#druvasecurityevents_cl) |
| **Used in Solutions** | [DruvaDataSecurityCloud](../solutions/druvadatasecuritycloud.md) |
| **Connector Definition Files** | [Druva_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud/Data%20Connectors/Druva_ccp/Druva_DataConnectorDefinition.json) |

Provides capability to ingest the Druva events from Druva APIs

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permission are required

**Custom Permissions:**
- **Druva API Access**: Druva API requires a client id and client secret to authenticate

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>Note: Configurations to connect to Druva Rest API

Step 1: Create credentials from Druva console. Refer this doc for steps:- https://help.druva.com/en/articles/8580838-create-and-manage-api-credentials

Step 2: Enter the hostname. For public cloud its apis.druva.com

Step 3: Enter client id and client secret key

**4. Connect to Druva API to start collecting logs in Microsoft Sentinel**

Provide required values:
- **Hostname**: Example: apis.druva.com
- **OAuth Configuration**:
  - Client ID
  - Client Secret
  - Click 'Connect' to authenticate

[← Back to Connectors Index](../connectors-index.md)
