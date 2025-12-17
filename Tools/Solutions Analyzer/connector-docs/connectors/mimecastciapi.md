# Mimecast Cloud Integrated

| | |
|----------|-------|
| **Connector ID** | `MimecastCIAPI` |
| **Publisher** | Mimecast |
| **Tables Ingested** | [`Cloud_Integrated_CL`](../tables-index.md#cloud_integrated_cl) |
| **Used in Solutions** | [Mimecast](../solutions/mimecast.md) |
| **Connector Definition Files** | [Mimecast_Cloud_Integrated_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Data%20Connectors/MimecastCloudIntegrated/Mimecast_Cloud_Integrated_FunctionApp.json) |

The data connector for [Mimecast Cloud Integrated](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to the Cloud Integrated inspection technologies within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Azure Subscription**: Azure Subscription with owner role is required to register an application in Microsoft Entra ID and assign role of contributor to app in resource group.
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: See the documentation to learn more about API on the [Rest API reference](https://integrations.mimecast.com/documentation/)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Resource group**

You need to have a resource group created with a subscription you are going to use.

**2. Functions app**

You need to have an Azure App registered for this connector to use
1. Application Id
2. Tenant Id
3. Client Id
4. Client Secret

>**NOTE:** This connector uses Azure Functions to connect to a Mimecast API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**3. Configuration:**

**STEP 1 - Configuration steps for the Mimecast API**

Go to ***Azure portal ---> App registrations ---> [your_app] ---> Certificates & secrets ---> New client secret*** and create a new secret (save the Value somewhere safe right away because you will not be able to preview it later)

**STEP 2 - Deploy Mimecast API Connector**

>**IMPORTANT:** Before deploying the Mimecast API connector, have the Mimecast API authorization key(s) or Token, readily available.

**STEP 3 - App Registration steps for the Application in Microsoft Entra ID**

 This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:
 1. Sign in to the [Azure portal](https://portal.azure.com/).
 2. Search for and select **Microsoft Entra ID**.
 3. Under **Manage**, select **App registrations > New registration**.
 4. Enter a display **Name** for your application.
 5. Select **Register** to complete the initial app registration.
 6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the **Application (client) ID** and **Tenant ID**. The client ID and Tenant ID is required as configuration parameters for the execution of TenableVM Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)

**STEP 4 - Add a client secret for application in Microsoft Entra ID**

 Sometimes called an application password, a client secret is a string value required for the execution of TenableVM Data Connector. Follow the steps in this section to create a new Client Secret:
 1. In the Azure portal, in **App registrations**, select your application.
 2. Select **Certificates & secrets > Client secrets > New client secret**.
 3. Add a description for your client secret.
 4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
 5. Select **Add**. 
 6. *Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page.* The secret value is required as configuration parameter for the execution of TenableVM Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret)

**STEP 5 - Get Object ID of your application in Microsoft Entra ID**

 After creating your app registration, follow the steps in this section to get Object ID:
 1. Go to **Microsoft Entra ID**.
 2. Select **Enterprise applications** from the left menu.
 3. Find your newly created application in the list (you can search by the name you provided).
 4. Click on the application.
 5. On the overview page, copy the **Object ID**. This is the **AzureEntraObjectId** needed for your ARM template role assignment.

**8. Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Mimecast Cloud Integrated Data connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-MimecastCI-azuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-MimecastCI-azuredeploy-gov)
2. Select the preferred **Subscription**, **Resource Group** and **Region**. 
3. Enter the below information : 

	 a. Location - The location in which the data collection rules and data collection endpoints should be deployed

	 b. WorkspaceName - Enter Microsoft Sentinel Workspace Name of Log Analytics workspace

	 c. AzureClientID - Enter Azure Client ID that you have created during app registration

	 d. AzureClientSecret - Enter Azure Client Secret that you have created during creating the client secret

	 e. AzureTenantID - Enter Azure Tenant ID of your Azure Active Directory

	 f. AzureEntraObjectID - Enter Object id of your Microsoft Entra App

	 g. MimecastBaseURL - Enter Base URL of Mimecast API 2.0 (e.g. https://api.services.mimecast.com)

	 h. MimecastClientID - Enter Mimecast Client ID for authentication

	 i. MimecastClientSecret - Enter Mimecast Client Secret for authentication

	 j. MimecastCITableName - Enter name of the table used to store Cloud Integrated data. Default is 'Cloud_Integrated'

	 k. StartDate - Enter the start date in the 'yyyy-mm-dd' format. If you do not provide a date, data from the last 60 days will be fetched automatically. Ensure that the date is in the past and properly formatted

	 l. Schedule - Please enter a valid Quartz cron-expression. (Example: 0 0 */1 * * *) Do not keep the value empty, minimum value is 10 minutes

	 m. LogLevel - Please add log level or log severity value. By default it is set to INFO

	 n. AppInsightsWorkspaceResourceId - Migrate Classic Application Insights to Log Analytic Workspace which is retiring by 29 Febraury 2024. Use 'Log Analytic Workspace-->Properties' blade having 'Resource ID' property value. This is a fully qualified resourceId which is in format '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}' 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

[← Back to Connectors Index](../connectors-index.md)
