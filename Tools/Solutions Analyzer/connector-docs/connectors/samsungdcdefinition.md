# Samsung Knox Asset Intelligence

| | |
|----------|-------|
| **Connector ID** | `SamsungDCDefinition` |
| **Publisher** | Samsung |
| **Tables Ingested** | [`Samsung_Knox_Application_CL`](../tables-index.md#samsung_knox_application_cl), [`Samsung_Knox_Audit_CL`](../tables-index.md#samsung_knox_audit_cl), [`Samsung_Knox_Network_CL`](../tables-index.md#samsung_knox_network_cl), [`Samsung_Knox_Process_CL`](../tables-index.md#samsung_knox_process_cl), [`Samsung_Knox_System_CL`](../tables-index.md#samsung_knox_system_cl), [`Samsung_Knox_User_CL`](../tables-index.md#samsung_knox_user_cl) |
| **Used in Solutions** | [Samsung Knox Asset Intelligence](../solutions/samsung-knox-asset-intelligence.md) |
| **Connector Definition Files** | [Template_Samsung.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence/Data%20Connectors/Template_Samsung.json) |

Samsung Knox Asset Intelligence Data Connector lets you centralize your mobile security events and logs in order to view customized insights using the Workbook template, and identify incidents based on Analytics Rules templates.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Entra app**: An Entra app needs to be registered and provisioned with ‘Microsoft Metrics Publisher’ role and configured with either Certificate or Client Secret as credentials for secure data transfer. See [the Log ingestion tutorial to learn more about Entra App creation, registration and credential configuration.](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

This Data Connector uses the Microsoft Log Ingestion API to push security events into Microsoft Sentinel from Samsung Knox Asset Intelligence (KAI) solution.

**2. STEP 1 - Create and register an Entra Application**

>**Note**: This Data Connector can support either Certificate-based or Client Secret-based authentication. For Certificate-based authentication, you can download the Samsung CA-signed certificate (public key) from [KAI documentation portal](https://docs.samsungknox.com/admin/knox-asset-intelligence/assets/samsung-knox-validation-certificate.crt). For Client Secret-based authentication, you can create the secret during the Entra application registration. Ensure you copy the Client Secret value as soon as it is generated.

>**IMPORTANT:** Save the values for Tenant (Directory) ID and Client (Application) ID. If Client Secret-based authentication is enabled, save Client Secret (Secret Value) associated with the Entra app.

**3. STEP 2 - Automate deployment of this Data Connector using the below Azure Resource Manager (ARM) template**

>**IMPORTANT:** Before deploying the Data Connector, copy the below Workspace name associated with your Microsoft Sentinel (also your Log Analytics) instance.
- **Workspace Name**: `WorkspaceName`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

1. Click the button below to install Samsung Knox Intelligence Solution. 

	[![DeployToAzure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-SamsungDCDefinition-azuredeploy)\n2. Provide the following required fields: Log Analytics Workspace Name, Log Analytics Workspace Location, Log Analytics Workspace Subscription (ID) and Log Analytics Workspace Resource Group.

**5. STEP 3 - Obtain Microsoft Sentinel Data Collection details**

Once the ARM template is deployed, navigate to Data Collection Rules https://portal.azure.com/#browse/microsoft.insights%2Fdatacollectionrules? and save values associated with the Immutable ID (DCR) and Data Collection Endpoint (DCE). 

>**IMPORTANT:** To enable end-to-end integration, information related to Microsoft Sentinel DCE and DCR are required for configuration in Samsung Knox Asset Intelligence portal (STEP 4). 

Ensure the Entra Application created in STEP 1 has permissions to use the DCR created in order to send data to the DCE. Please refer to https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#assign-permissions-to-the-dcr to assign permissions accordingly.

**6. STEP 4 - Connect to Samsung Knox Asset Intelligence solution to configure Microsoft Sentinel to push select Knox Security Events as Alerts**

1. Login to [Knox Asset Intelligence administration portal](https://central.samsungknox.com/kaiadmin/dai/home) and navigate to **Dashboard Settings**; this is available at the top-right corner of the Portal.
>  **Note**: Ensure the login user has access to 'Security' and 'Manage dashboard view and data collection' permissions.

2. Click on Security tab to view settings for Microsoft Sentinel Integration and Knox Security Logs.

3. In the Security Operations Integration page, toggle on **'Enable Microsoft Sentinel Integration'** and enter appropriate values in the required fields.

  >a. Based on the authentication method used, refer to information saved from STEP 1 while registering the Entra application. 

  >b. For Microsoft Sentinel DCE and DCR, refer to the information saved from STEP 3. 

4. Click on **'Test Connection'** and ensure the connection is successful.

5. Before you can Save, configure Knox Security Logs by selecting either  Essential or Advanced configuration **(default: Essential).**

6. To complete the Microsoft Sentinel integration, click **'Save'**.

[← Back to Connectors Index](../connectors-index.md)
