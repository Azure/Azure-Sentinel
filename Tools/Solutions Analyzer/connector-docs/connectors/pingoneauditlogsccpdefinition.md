# Ping One (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `PingOneAuditLogsCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`PingOne_AuditActivitiesV2_CL`](../tables-index.md#pingone_auditactivitiesv2_cl) |
| **Used in Solutions** | [PingOne](../solutions/pingone.md) |
| **Connector Definition Files** | [PingOneAuditLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne/Data%20Connectors/PingOneAuditLogs_ccp/PingOneAuditLogs_DataConnectorDefinition.json) |

This connector ingests **audit activity logs** from the PingOne Identity platform into Microsoft Sentinel using a Codeless Connector Framework.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Ping One connector to Microsoft Sentinel**
Before connecting to PingOne, ensure the following prerequisites are completed. Refer to the [document](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne/README.md) for detailed setup instructions, including how to obtain client credentials and the environment ID.
#### 1. Client Credentials 
 You'll need client credentials, including your client id and client secret.
#### 2. Environment Id  
 To generate token and gather logs from audit activities endpoint
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Environment ID**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add domain**

*Add domain*

When you click the "Add domain" button in the portal, a configuration form will open. You'll need to provide:

- **Client ID** (optional): Enter ID of the client
- **Client Secret** (optional): Enter your secret key
- **Environment ID** (optional): Enter your environment Id 
- **Api domain** (optional): Enter your Api domain Eg.( pingone.com,pingone.eu etc )depending on the region credentials created for 

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
