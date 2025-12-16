# OneLogin IAM Platform (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `OneLoginIAMLogsCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`OneLoginEventsV2_CL`](../tables-index.md#onelogineventsv2_cl), [`OneLoginUsersV2_CL`](../tables-index.md#oneloginusersv2_cl) |
| **Used in Solutions** | [OneLoginIAM](../solutions/oneloginiam.md) |
| **Connector Definition Files** | [OneLoginIAMLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneLoginIAM/Data%20Connectors/OneLoginIAMLogs_ccp/OneLoginIAMLogs_ConnectorDefinition.json) |

The [OneLogin](https://www.onelogin.com/) data connector provides the capability to ingest common OneLogin IAM Platform events into Microsoft Sentinel through REST API by using OneLogin [Events API](https://developers.onelogin.com/api-docs/1/events/get-events) and OneLogin [Users API](https://developers.onelogin.com/api-docs/1/users/get-users). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **OneLogin IAM API Credentials**: To create API Credentials follow the document link provided here, [Click Here](https://developers.onelogin.com/api-docs/1/getting-started/working-with-api-credentials). 
 Make sure to have an account type of either account owner or administrator to create the API credentials. 
 Once you create the API Credentials you get your Client ID and Client Secret.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect OneLogin IAM Platform to Microsoft Sentinel**

To ingest data from OneLogin IAM to Microsoft Sentinel, you have to click on Add Domain button below then you get a pop up to fill the details, provide the required information and click on Connect. You can see the domain endpoints connected in the grid.
>
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Endpoint**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add domain**

*Add domain*

When you click the "Add domain" button in the portal, a configuration form will open. You'll need to provide:

- **OneLogin Domain** (optional): Enter your Company's OneLogin Domain
- **Client ID** (optional): Enter your Client ID
- **Client Secret** (optional): Enter your Client Secret

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
