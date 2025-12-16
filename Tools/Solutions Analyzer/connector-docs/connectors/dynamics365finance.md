# Dynamics 365 Finance and Operations

| | |
|----------|-------|
| **Connector ID** | `Dynamics365Finance` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`FinanceOperationsActivity_CL`](../tables-index.md#financeoperationsactivity_cl) |
| **Used in Solutions** | [Microsoft Business Applications](../solutions/microsoft-business-applications.md) |
| **Connector Definition Files** | [DynamicsFinOps_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Data%20Connectors/DynamicsFinOpsPollerConnector/DynamicsFinOps_DataConnectorDefinition.json) |

Dynamics 365 for Finance and Operations is a comprehensive Enterprise Resource Planning (ERP) solution that combines financial and operational capabilities to help businesses manage their day-to-day operations. It offers a range of features that enable businesses to streamline workflows, automate tasks, and gain insights into operational performance.



The Dynamics 365 Finance and Operations data connector ingests Dynamics 365 Finance and Operations admin activities and audit logs as well as user business process and application activities logs into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Microsoft Entra app registration**: Application client ID and secret used to access Dynamics 365 Finance and Operations.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>Connectivity to Finance and Operations requires a Microsoft Entra app registration (client ID and secret). You'll also need the Microsoft Entra tenant ID and the Finance Operations Organization URL.

To enable data collection, create a role in Dynamics 365 Finance and Operations with permissions to view the Database Log entity. Assign this role to a dedicated Finance and Operations user, mapped to the client ID of a Microsoft Entra app registration. Follow these steps to complete the process:

**2. Step 1 - Microsoft Entra app registration**

1. Navigate to the [Microsoft Entra portal](https://entra.microsoft.com). 
2. Under Applications, click on **App Registrations** and create a new app registration (leave all defaults).
3. Open the new app registration and create a new secret.
4. Retain the **Tenant ID**, **Application (client) ID**, and **Client secret** for later use.

**3. Step 2 - Create a role for data collection in Finance and Operations**

1. In the Finance and Operations portal, navigate to **Workspaces > System administration** and click **Security Configuration**
2. Under **Roles** click **Create new** and give the new role a name e.g. Database Log Viewer.
3. Select the new role in the list of roles and click **Privileges** and than **Add references**.
4. Select **Database log Entity View** from the list of privileges.
5. Click on **Unpublished objects** and then **Publish all** to publish the role.

**4. Step 3 - Create a user for data collection in Finance and Operations**

1. In the Finance and Operations portal, navigate to **Modules > System administration** and click **Users**
2. Create a new user and assign the role created in the previous step to the user.

**5. Step 4 - Register the Microsoft Entra app in Finance and Operations**

1. In the F&O portal, navigate to **System administration > Setup > Microsoft Entra applications** (Azure Active Directory applications)
2. Create a new entry in the table. In the **Client Id** field, enter the application ID of the app registered in Step 1.
3. In the **Name** field, enter a name for the application.
4. In the **User ID** field, select the user ID created in the previous step.

**6. Connect events from Dyanmics 365 Finance and Operations to Microsoft Sentinel**

Connect using client credentials
**Dynamics 365 Finance and Operations connection**

When you click the "Add environment" button in the portal, a configuration form will open. You'll need to provide:

*Environment details*

- **Microsoft Entra tenant ID.** (optional): Tenant ID (GUID)
- **App registration client ID** (optional): Finance and Operations client ID
- **App registration client secret** (optional): Finance and Operations client secret
- **Finance and Operations organization URL** (optional): https://dynamics-dev.axcloud.dynamics.com

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.


**7. Organizations**

Each row represents an Finance and Operations connection
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Environment URL**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

[← Back to Connectors Index](../connectors-index.md)
