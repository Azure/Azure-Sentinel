# SAP S/4HANA Cloud Public Edition

| | |
|----------|-------|
| **Connector ID** | `SAPS4PublicAlerts` |
| **Publisher** | SAP |
| **Tables Ingested** | [`ABAPAuditLog`](../tables-index.md#abapauditlog) |
| **Used in Solutions** | [SAP S4 Cloud Public Edition](../solutions/sap-s4-cloud-public-edition.md) |
| **Connector Definition Files** | [SAPS4Public_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20S4%20Cloud%20Public%20Edition/Data%20Connectors/SAPS4PublicPollerConnector/SAPS4Public_connectorDefinition.json) |

The SAP S/4HANA Cloud Public Edition (GROW with SAP) data connector enables ingestion of SAP's security audit log into the Microsoft Sentinel Solution for SAP, supporting cross-correlation, alerting, and threat hunting. Looking for alternative authentication mechanisms? See [here](https://github.com/Azure-Samples/Sentinel-For-SAP-Community/tree/main/integration-artifacts).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Client Id and Client Secret for Audit Retrieval API**: Enable API access in BTP.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**Step 1 - Configuration steps for SAP S/4HANA Cloud Public Edition**

To connect to SAP S/4HANA Cloud Public Edition, you will need:

1. Configure a communication arrangement for communication scenario **[SAP_COM_0750](https://help.sap.com/docs/SAP_S4HANA_CLOUD/0f69f8fb28ac4bf48d2b57b9637e81fa/a93dca70e2ce43d19ac93e3e5531e37d.html)**  

2. SAP S/4HANA Cloud Public Edition tenant **API URL**
3. Valid **communication user (username and password)** for your SAP S/4HANA Cloud system
4. **Appropriate authorizations** to access audit log data via OData services

>**NOTE:** This connector supports Basic authentication. Looking for alternative authentication mechanisms? See [here](https://github.com/Azure-Samples/Sentinel-For-SAP-Community/tree/main/integration-artifacts)

**2. Connect events from SAP S/4HANA Cloud Public Edition to Microsoft Sentinel Solution for SAP**

Connect using Basic authentication
**S/4HANA Cloud Public Edition connection**

When you click the "Add account" button in the portal, a configuration form will open. You'll need to provide:

*Account Details*

- **Username** (optional): Enter your SAP S/4HANA Cloud username
- **Password** (optional): Enter your SAP S/4HANA Cloud password
- **SAP S/4HANA Cloud API URL** (optional): https://my123456-api.s4hana.cloud.sap

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.


**3. S/4HANA Cloud Public Edition connections**

Each row represents a connected S/4HANA Cloud Public Edition system
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **S/4HANA Cloud API endpoint**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

[← Back to Connectors Index](../connectors-index.md)
