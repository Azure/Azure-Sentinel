# Netskope Data Connector

| | |
|----------|-------|
| **Connector ID** | `NetskopeDataConnector` |
| **Publisher** | Netskope |
| **Tables Ingested** | [`Netskope_WebTx_metrics_CL`](../tables-index.md#netskope_webtx_metrics_cl), [`alertscompromisedcredentialdata_CL`](../tables-index.md#alertscompromisedcredentialdata_cl), [`alertsctepdata_CL`](../tables-index.md#alertsctepdata_cl), [`alertsdlpdata_CL`](../tables-index.md#alertsdlpdata_cl), [`alertsmalsitedata_CL`](../tables-index.md#alertsmalsitedata_cl), [`alertsmalwaredata_CL`](../tables-index.md#alertsmalwaredata_cl), [`alertspolicydata_CL`](../tables-index.md#alertspolicydata_cl), [`alertsquarantinedata_CL`](../tables-index.md#alertsquarantinedata_cl), [`alertsremediationdata_CL`](../tables-index.md#alertsremediationdata_cl), [`alertssecurityassessmentdata_CL`](../tables-index.md#alertssecurityassessmentdata_cl), [`alertsubadata_CL`](../tables-index.md#alertsubadata_cl), [`eventsapplicationdata_CL`](../tables-index.md#eventsapplicationdata_cl), [`eventsauditdata_CL`](../tables-index.md#eventsauditdata_cl), [`eventsconnectiondata_CL`](../tables-index.md#eventsconnectiondata_cl), [`eventsincidentdata_CL`](../tables-index.md#eventsincidentdata_cl), [`eventsnetworkdata_CL`](../tables-index.md#eventsnetworkdata_cl), [`eventspagedata_CL`](../tables-index.md#eventspagedata_cl) |
| **Used in Solutions** | [Netskopev2](../solutions/netskopev2.md) |
| **Connector Definition Files** | [Netskope_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Data%20Connectors/NetskopeDataConnector/Netskope_FunctionApp.json) |

The [Netskope](https://docs.netskope.com/en/netskope-help/admin-console/rest-api/rest-api-v2-overview-312207/) data connector provides the following capabilities: 

 1. NetskopeToAzureStorage : 

 >* Get the Netskope Alerts and Events data from Netskope and ingest to Azure storage. 

 2. StorageToSentinel : 

 >* Get the Netskope Alerts and Events data from Azure storage and ingest to custom log table in log analytics workspace. 

 3. WebTxMetrics : 

 >* Get the WebTxMetrics data from Netskope and ingest to custom log table in log analytics workspace.





 For more details of REST APIs refer to the below documentations: 

 1. Netskope API documentation: 

> https://docs.netskope.com/en/netskope-help/admin-console/rest-api/rest-api-v2-overview-312207/ 

 2. Azure storage documentation: 

> https://learn.microsoft.com/azure/storage/common/storage-introduction 

 3. Microsoft log analytic documentation: 

> https://learn.microsoft.com/azure/azure-monitor/logs/log-analytics-overview

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Azure Subscription**: Azure Subscription with owner role is required to register an application in azure active directory() and assign role of contributor to app in resource group.
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **Netskope Tenant** and **Netskope API Token** is required.  See the documentation to learn more about API on the [Rest API reference](https://docs.netskope.com/en/netskope-help/admin-console/rest-api/rest-api-v2-overview-312207/)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Netskope APIs to pull its Alerts and Events data into custom log table. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - App Registration steps for the Application in Microsoft Entra ID**

 This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:
 1. Sign in to the [Azure portal](https://portal.azure.com/).
 2. Search for and select **Microsoft Entra ID**.
 3. Under **Manage**, select **App registrations > New registration**.
 4. Enter a display **Name** for your application.
 5. Select **Register** to complete the initial app registration.
 6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the **Application (client) ID** and **Tenant ID**. The client ID and Tenant ID is required as configuration parameters for the execution of the TriggersSync playbook. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)

**STEP 2 - Add a client secret for application in Microsoft Entra ID**

 Sometimes called an application password, a client secret is a string value required for the execution of TriggersSync playbook. Follow the steps in this section to create a new Client Secret:
 1. In the Azure portal, in **App registrations**, select your application.
 2. Select **Certificates & secrets > Client secrets > New client secret**.
 3. Add a description for your client secret.
 4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
 5. Select **Add**. 
 6. *Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page.* The secret value is required as configuration parameter for the execution of TriggersSync playbook. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret)

**STEP 3 - Assign role of Contributor to application in Microsoft Entra ID**

 Follow the steps in this section to assign the role:
 1. In the Azure portal, Go to **Resource Group** and select your resource group.
 2. Go to **Access control (IAM)** from left panel.
 3. Click on **Add**, and then select **Add role assignment**.
 4. Select **Contributor** as role and click on next.
 5. In **Assign access to**, select `User, group, or service principal`.
 6. Click on **add members** and type **your app name** that you have created and select it.
 7. Now click on **Review + assign** and then again click on **Review + assign**. 

> **Reference link:** [https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal](https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal)

**STEP 4 - Steps to create/get Credentials for the Netskope account** 

 Follow the steps in this section to create/get **Netskope Hostname** and **Netskope API Token**:
 1. Login to your **Netskope Tenant** and go to the **Settings menu** on the left navigation bar.
 2. Click on Tools and then **REST API v2**
 3. Now, click on the new token button. Then it will ask for token name, expiration duration and the endpoints that you want to fetch data from.
 5. Once that is done click the save button, the token will be generated. Copy the token and save at a secure place for further usage.

**STEP 5 - Steps to create the azure functions for Netskope Alerts and Events Data Collection**

>**IMPORTANT:** Before deploying Netskope data connector, have the  Workspace ID and Workspace Primary Key (can be copied from the following) readily available.., as well as the Netskope API Authorization Key(s).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

Using the ARM template deploy the function apps for ingestion of Netskope events and alerts data to Sentinel.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-NetskopeV2-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the below information : 
		Netskope HostName 
		Netskope API Token 
		Select Yes in Alerts and Events types dropdown for that endpoint you want to fetch Alerts and Events 
		Log Level 
		Workspace ID 
		Workspace Key 
4. Click on **Review+Create**. 
5. Then after validation click on **Create** to deploy.

[← Back to Connectors Index](../connectors-index.md)
