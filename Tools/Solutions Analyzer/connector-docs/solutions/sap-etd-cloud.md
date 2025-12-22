# SAP ETD Cloud

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | SAP |
| **Support Tier** | Partner |
| **Support Link** | [https://help.sap.com/docs/SAP_ENTERPRISE_THREAT_DETECTION_CLOUD_EDITION](https://help.sap.com/docs/SAP_ENTERPRISE_THREAT_DETECTION_CLOUD_EDITION) |
| **Categories** | domains |
| **First Published** | 2025-02-17 |
| **Last Updated** | 2025-09-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20ETD%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20ETD%20Cloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SAP Enterprise Threat Detection, cloud edition](../connectors/sapetdalerts.md)

**Publisher:** SAP

The SAP Enterprise Threat Detection, cloud edition (ETD) data connector enables ingestion of security alerts from ETD into Microsoft Sentinel, supporting cross-correlation, alerting, and threat hunting.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Client Id and Client Secret for ETD Retrieval API**: Enable API access in ETD.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**Step 1 - Configuration steps for the SAP ETD Audit Retrieval API**

Follow the steps provided by SAP [see ETD docs](https://help.sap.com/docs/ETD/sap-business-technology-platform/audit-log-retrieval-api-for-global-accounts-in-cloud-foundry-environment/). Take a note of the **url** (Audit Retrieval API URL), **uaa.url** (User Account and Authentication Server url) and the associated **uaa.clientid**.

>**NOTE:** You can onboard one or more ETD subaccounts by following the steps provided by SAP [see ETD docs](https://help.sap.com/docs/ETD/sap-business-technology-platform/audit-log-retrieval-api-usage-for-subaccounts-in-cloud-foundry-environment/). Add a connection for each subaccount.

>**TIP:** Use the [shared blog series](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/sap-enterprise-threat-detection-cloud-edition-joins-forces-with-microsoft/ba-p/13942075) for additional info.

**2. Connect events from SAP ETD to Microsoft Sentinel**

Connect using OAuth client credentials
**ETD connection**

When you click the "Add account" button in the portal, a configuration form will open. You'll need to provide:

*Account Details*

- **SAP ETD Client ID** (optional): Client ID
- **SAP ETD Client Secret** (optional): Client Secret
- **Authorization server URL (UAA server)** (optional): https://your-tenant.authentication.region.hana.ondemand.com/oauth/token
- **SAP ETD data retrieval API URL** (optional): https://your-etd-cloud-data-retrieval-service.cfapps.region.hana.ondemand.com

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.


**3. ETD accounts**

Each row represents a connected ETD account
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Data retrieval endpoint**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

| | |
|--------------------------|---|
| **Tables Ingested** | `SAPETDAlerts_CL` |
| | `SAPETDInvestigations_CL` |
| **Connector Definition Files** | [SAPETD_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20ETD%20Cloud/Data%20Connectors/SAPETD_PUSH_CCP/SAPETD_connectorDefinition.json) |

[→ View full connector details](../connectors/sapetdalerts.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SAPETDAlerts_CL` | [SAP Enterprise Threat Detection, cloud edition](../connectors/sapetdalerts.md) |
| `SAPETDInvestigations_CL` | [SAP Enterprise Threat Detection, cloud edition](../connectors/sapetdalerts.md) |

[← Back to Solutions Index](../solutions-index.md)
