# SAP BTP

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2023-04-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SAP BTP](../connectors/sapbtpauditevents.md)

**Publisher:** Microsoft

SAP Business Technology Platform (SAP BTP) brings together data management, analytics, artificial intelligence, application development, automation, and integration in one, unified environment.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Client Id and Client Secret for Audit Retrieval API**: Enable API access in BTP.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**Step 1 - Configuration steps for the SAP BTP Audit Retrieval API**

Follow the steps provided by SAP [see Audit Log Retrieval API for Global Accounts in the Cloud Foundry Environment](https://help.sap.com/docs/btp/sap-business-technology-platform/audit-log-retrieval-api-for-global-accounts-in-cloud-foundry-environment/). Take a note of the **url** (Audit Retrieval API URL), **uaa.url** (User Account and Authentication Server url) and the associated **uaa.clientid**.

>**NOTE:** You can onboard one or more BTP subaccounts by following the steps provided by SAP [see Audit Log Retrieval API Usage for Subaccounts in the Cloud Foundry Environment](https://help.sap.com/docs/btp/sap-business-technology-platform/audit-log-retrieval-api-usage-for-subaccounts-in-cloud-foundry-environment/). Add a connection for each subaccount.

**2. Connect events from SAP BTP to Microsoft Sentinel**

Connect using OAuth client credentials
**BTP connection**

When you click the "Add account" button in the portal, a configuration form will open. You'll need to provide:

*Account Details*

- **Subaccount name (e.g. Contoso). This will be projected to the InstanceName column.** (optional): no space or special character allowed!
- **SAP BTP Client ID** (optional): Client ID
- **SAP BTP Client Secret** (optional): Client Secret
- **Authorization server URL (UAA server)** (optional): https://your-tenant.authentication.region.hana.ondemand.com
- **Audit Retrieval API URL** (optional): https://auditlog-management.cfapps.region.hana.ondemand.com

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.


**3. Subaccounts**

Each row represents a connected subaccount
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Subaccount Name**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

| | |
|--------------------------|---|
| **Tables Ingested** | `SAPBTPAuditLog_CL` |
| **Connector Definition Files** | [SAPBTP_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP/Data%20Connectors/SAPBTPPollerConnector/SAPBTP_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/sapbtpauditevents.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SAPBTPAuditLog_CL` | [SAP BTP](../connectors/sapbtpauditevents.md) |

[← Back to Solutions Index](../solutions-index.md)
