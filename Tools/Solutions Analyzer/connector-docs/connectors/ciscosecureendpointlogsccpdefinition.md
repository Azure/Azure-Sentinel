# Cisco Secure Endpoint (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `CiscoSecureEndpointLogsCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables-index.md#ciscosecureendpointauditlogsv2_cl), [`CiscoSecureEndpointEventsV2_CL`](../tables-index.md#ciscosecureendpointeventsv2_cl) |
| **Used in Solutions** | [Cisco Secure Endpoint](../solutions/cisco-secure-endpoint.md) |
| **Connector Definition Files** | [CiscoSecureEndpointLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Data%20Connectors/CiscoSecureEndpointLogs_ccp/CiscoSecureEndpointLogs_ConnectorDefinition.json) |

The Cisco Secure Endpoint (formerly AMP for Endpoints) data connector provides the capability to ingest Cisco Secure Endpoint [audit logs](https://developer.cisco.com/docs/secure-endpoint/auditlog/) and [events](https://developer.cisco.com/docs/secure-endpoint/v1-api-reference-event/) into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Cisco Secure Endpoint API Credentials/Regions**: To create API Credentials and to understand the regions, follow the document link provided here. [Click here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Data%20Connectors/README.md).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Cisco Secure Endpoint to Microsoft Sentinel**

To ingest data from Cisco Secure Endpoint to Microsoft Sentinel, you have to click on Add Account button below, then you get a pop up to fill the details like Email, Organization, Client ID, API Key and Region, provide the required information and click on Connect. You can see the connected organizations/emails in the below grid.
>
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Organization**
- **Email**
- **Endpoint**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add Account**

*Add Account*

When you click the "Add Account" button in the portal, a configuration form will open. You'll need to provide:

- **Cisco Secure Endpoint Email** (optional): Enter your Cisco Email
- **Cisco Secure Endpoint Organization** (optional): Enter the name of your Organization
- **Cisco Secure Endpoint Client ID** (optional): Enter your Client ID
- **Cisco Secure Endpoint API Key** (optional): Enter your API Key
- **Cisco Secure Endpoint Region** (optional): Enter the region you want to connect

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
