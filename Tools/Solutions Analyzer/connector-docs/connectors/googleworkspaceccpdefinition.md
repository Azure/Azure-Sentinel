# Google Workspace Activities (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `GoogleWorkspaceCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`GoogleWorkspaceReports`](../tables-index.md#googleworkspacereports) |
| **Used in Solutions** | [GoogleWorkspaceReports](../solutions/googleworkspacereports.md) |
| **Connector Definition Files** | [GoogleWorkspaceReports_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleWorkspaceReports/Data%20Connectors/GoogleWorkspaceTemplate_ccp/GoogleWorkspaceReports_DataConnectorDefinition.json) |

The [Google Workspace](https://workspace.google.com/) Activities data connector provides the capability to ingest Activity Events from [Google Workspace API](https://developers.google.com/admin-sdk/reports/reference/rest/v1/activities/list) into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Google Workspace API access**: Access to the Google Workspace activities API through Oauth are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to Google Workspace to start collecting user activity logs into Microsoft Sentinel**
#### Configuration steps for the Google Reports API

1. Login to Google cloud console with your Workspace Admin credentials https://console.cloud.google.com.
2. Using the search option (available at the top middle), Search for ***APIs & Services***
3. From ***APIs & Services*** -> ***Enabled APIs & Services***, enable **Admin SDK API** for this project.
 4. Go to ***APIs & Services*** -> ***OAuth Consent Screen***. If not already configured, create a OAuth Consent Screen with the following steps:
	 1. Provide App Name and other mandatory information.
	 2. Add authorized domains with API Access Enabled.
	 3. In Scopes section, add **Admin SDK API** scope.
	 4. In Test Users section, make sure the domain admin account is added.
 5. Go to ***APIs & Services*** -> ***Credentials*** and create OAuth 2.0 Client ID
	 1. Click on Create Credentials on the top and select Oauth client Id.
	 2. Select Web Application from the Application Type drop down.
	 3. Provide a suitable name to the Web App and add https://portal.azure.com/TokenAuthorize/ExtensionName/Microsoft_Azure_Security_Insights as the Authorized redirect URIs.
	 4. Once you click Create, you will be provided with the Client ID and Client Secret. 
	Copy these values and use them in the configuration steps below.
Configure steps for the Google Reports API oauth access. Then, provide the required information below and click on Connect.
>
- **OAuth Configuration**:
  - Client ID
  - Client Secret
  - Click 'Connect' to authenticate
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Name**
- **ID**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

[← Back to Connectors Index](../connectors-index.md)
