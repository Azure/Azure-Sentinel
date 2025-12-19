# Palo Alto Cortex Xpanse CCF

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-12-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Cortex%20Xpanse%20CCF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Cortex%20Xpanse%20CCF) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Palo Alto Cortex Xpanse (via Codeless Connector Framework)](../connectors/paloaltoexpanseccpdefinition.md)

**Publisher:** Microsoft

The Palo Alto Cortex Xpanse data connector ingests alerts data into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

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

| | |
|--------------------------|---|
| **Tables Ingested** | `CortexXpanseAlerts_CL` |
| **Connector Definition Files** | [CortexXpanse_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Cortex%20Xpanse%20CCF/Data%20Connectors/CortexXpanse_ccp/CortexXpanse_ConnectorDefinition.json) |

[→ View full connector details](../connectors/paloaltoexpanseccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CortexXpanseAlerts_CL` | [Palo Alto Cortex Xpanse (via Codeless Connector Framework)](../connectors/paloaltoexpanseccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
