# Palo Alto Cortex Xpanse (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `PaloAltoExpanseCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CortexXpanseAlerts_CL`](../tables-index.md#cortexxpansealerts_cl) |
| **Used in Solutions** | [Palo Alto Cortex Xpanse CCF](../solutions/palo-alto-cortex-xpanse-ccf.md) |
| **Connector Definition Files** | [CortexXpanse_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Cortex%20Xpanse%20CCF/Data%20Connectors/CortexXpanse_ccp/CortexXpanse_ConnectorDefinition.json) |

The Palo Alto Cortex Xpanse data connector ingests alerts data into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Palo Alto Xpanse to Microsoft Sentinel**

To ingest data from Palo Alto Cortex Xpanse to Microsoft Sentinel, click on **Add Domain**. Fill in the required details in the pop-up and click Connect. You will see connected domain endpoints in the grid below. To get the Auth ID and API Key, go to **Settings → Configuration → Integrations → API Keys** in the Cortex Xpanse portal and generate new credentials.
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

- **Domain Name** (optional): e.g., example.crtx.us.paloaltonetworks.com
- **API Key** (optional): Enter your Palo Alto Xpanse API Key
- **Xpanse Auth ID** (optional): Enter your Xpanse Auth ID

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
