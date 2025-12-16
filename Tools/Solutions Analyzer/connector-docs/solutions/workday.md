# Workday

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-02-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workday](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workday) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Workday User Activity](../connectors/workdayccpdefinition.md)

**Publisher:** Microsoft

The [Workday](https://www.workday.com/) User Activity data connector provides the capability to ingest User Activity Logs from [Workday API](https://community.workday.com/sites/default/files/file-hosting/restapi/index.html#privacy/v1/get-/activityLogging) into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Workday User Activity API access**: Access to the Workday user activity API through Oauth are required. The API Client needs to have the scope: System and it needs to be authorized by an account with System Auditing permissions.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to Workday to start collecting user activity logs in Microsoft Sentinel**

1) In Workday, access the "Edit Tenant Setup - Security" task, verify "OAuth 2.0 Settings" section, make sure that the "OAuth 2.0 Clients Enabled" check box is ticked. 
 2) In Workday, access the "Edit Tenant Setup - System" task, verify "User Activity Logging" section, make sure that the "Enable User Activity Logging" check box is ticked. 
 3) In Workday, access the "Register API Client" task.
 4) Define the Client Name, select the "Client Grant Type": "Authorization Code Grant" and then select "Access Token Type": "Bearer"
 5) Enter the "Redirection URI": https://portal.azure.com/TokenAuthorize/ExtensionName/Microsoft_Azure_Security_Insights 
 6) In section "Scope (Functional Areas)", select "System" and click OK at the bottom 
 7) Copy the Client ID and Client Secret before navigating away from the page, and store it securely. 
 8) In Sentinel, in the connector page - provide required Token, Authorization and User Activity Logs Endpoints, along with Client ID and Client Secret from previous step. Then click "Connect". 
 9) A Workday pop up will appear to complete the OAuth2 authentication and authorization of the API client. Here you need to provide credentials for Workday account with "System Auditing" permissions in Workday (can be either Workday account or Integration System User). 
 10) Once that's complete, the message will be displayed to authorize your API client
- **Token Endpoint**: https://wd2-impl-services1.workday.com/ccx/oauth2/{tenantName}/token
- **Authorization Endpoint**: https://impl.workday.com/{tenantName}/authorize
- **User Activity Logs Endpoint, it ends with /activityLogging **: https://wd2-impl-services1.workday.com/ccx/api/privacy/v1/{tenantName}/activityLogging
- **OAuth Configuration**:
  - Client ID
  - Client Secret
  - Click 'Connect' to authenticate

| | |
|--------------------------|---|
| **Tables Ingested** | `ASimAuditEventLogs` |
| **Connector Definition Files** | [Workday_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workday/Data%20Connectors/Workday_ccp/Workday_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/workdayccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ASimAuditEventLogs` | [Workday User Activity](../connectors/workdayccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
