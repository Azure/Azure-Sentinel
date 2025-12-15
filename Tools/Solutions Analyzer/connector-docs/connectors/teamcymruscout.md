# Team Cymru Scout Data Connector

| | |
|----------|-------|
| **Connector ID** | `TeamCymruScout` |
| **Publisher** | Team Cymru Scout |
| **Tables Ingested** | [`Cymru_Scout_Account_Usage_Data_CL`](../tables-index.md#cymru_scout_account_usage_data_cl), [`Cymru_Scout_Domain_Data_CL`](../tables-index.md#cymru_scout_domain_data_cl), [`Cymru_Scout_IP_Data_Communications_CL`](../tables-index.md#cymru_scout_ip_data_communications_cl), [`Cymru_Scout_IP_Data_Details_CL`](../tables-index.md#cymru_scout_ip_data_details_cl), [`Cymru_Scout_IP_Data_Fingerprints_CL`](../tables-index.md#cymru_scout_ip_data_fingerprints_cl), [`Cymru_Scout_IP_Data_Foundation_CL`](../tables-index.md#cymru_scout_ip_data_foundation_cl), [`Cymru_Scout_IP_Data_OpenPorts_CL`](../tables-index.md#cymru_scout_ip_data_openports_cl), [`Cymru_Scout_IP_Data_PDNS_CL`](../tables-index.md#cymru_scout_ip_data_pdns_cl), [`Cymru_Scout_IP_Data_Summary_Certs_CL`](../tables-index.md#cymru_scout_ip_data_summary_certs_cl), [`Cymru_Scout_IP_Data_Summary_Details_CL`](../tables-index.md#cymru_scout_ip_data_summary_details_cl), [`Cymru_Scout_IP_Data_Summary_Fingerprints_CL`](../tables-index.md#cymru_scout_ip_data_summary_fingerprints_cl), [`Cymru_Scout_IP_Data_Summary_OpenPorts_CL`](../tables-index.md#cymru_scout_ip_data_summary_openports_cl), [`Cymru_Scout_IP_Data_Summary_PDNS_CL`](../tables-index.md#cymru_scout_ip_data_summary_pdns_cl), [`Cymru_Scout_IP_Data_x509_CL`](../tables-index.md#cymru_scout_ip_data_x509_cl) |
| **Used in Solutions** | [Team Cymru Scout](../solutions/team-cymru-scout.md) |
| **Connector Definition Files** | [TeamCymruScout_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Data%20Connectors/TeamCymruScout/TeamCymruScout_API_FunctionApp.json) |

The [TeamCymruScout](https://scout.cymru.com/) Data Connector allows users to bring Team Cymru Scout IP, domain and account usage data in Microsoft Sentinel for enrichment.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Permission to assign a role to the registered application**: Permission to assign a role to the registered application in Microsoft Entra ID is required.
- **Team Cymru Scout Credentials/permissions**: Team Cymru Scout account credentials(Username, Password) is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Team Cymru Scout API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Steps to Create Team Cymru Scout API Key**

 Follow these instructions to create a Team Cymru Scout API Key.
 1. Refer to the [API Keys](https://scout.cymru.com/docs/api#api-keys) document to generate an API key to use as an alternate form of authorization.

**STEP 2 - App Registration steps for the Application in Microsoft Entra ID**

 This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:
 1. Sign in to the [Azure portal](https://portal.azure.com/).
 2. Search for and select **Microsoft Entra ID**.
 3. Under **Manage**, select **App registrations > New registration**.
 4. Enter a display **Name** for your application.
 5. Select **Register** to complete the initial app registration.
 6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the **Application (client) ID** and **Tenant ID**. The client ID and Tenant ID is required as configuration parameters for the execution of TeamCymruScout Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)

**STEP 3 - Add a client secret for application in Microsoft Entra ID**

 Sometimes called an application password, a client secret is a string value required for the execution of TeamCymruScout Data Connector. Follow the steps in this section to create a new Client Secret:
 1. In the Azure portal, in **App registrations**, select your application.
 2. Select **Certificates & secrets > Client secrets > New client secret**.
 3. Add a description for your client secret.
 4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
 5. Select **Add**. 
 6. *Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page.* The secret value is required as configuration parameter for the execution of TeamCymruScout Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret)

**STEP 4 - Get Object ID of your application in Microsoft Entra ID**

 After creating your app registration, follow the steps in this section to get Object ID:
 1. Go to **Microsoft Entra ID**.
 2. Select **Enterprise applications** from the left menu.
 3. Find your newly created application in the list (you can search by the name you provided).
 4. Click on the application.
 5. On the overview page, copy the **Object ID**. This is the **AzureEntraObjectId** needed for your ARM template role assignment.

**STEP 5 - Assign role of Contributor to application in Microsoft Entra ID**

 Follow the steps in this section to assign the role:
 1. In the Azure portal, Go to **Resource Group** and select your resource group.
 2. Go to **Access control (IAM)** from left panel.
 3. Click on **Add**, and then select **Add role assignment**.
 4. Select **Contributor** as role and click on next.
 5. In **Assign access to**, select `User, group, or service principal`.
 6. Click on **add members** and type **your app name** that you have created and select it.
 7. Now click on **Review + assign** and then again click on **Review + assign**. 

> **Reference link:** [https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal](https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal)

**STEP 6 - Upload csv with indictaors in Watchlist**

 Follow the steps in this section to upload csv containing indicators in watchlist:
 1. In the Azure portal, Go to **Microsoft Sentinel** and select your workspace.
 2. Go to **Watchlist** under **Configuration** section from left panel.
 3. Click on **TeamCymruScoutDomainData**, and then select **Bulk update** from **Update watchlist**.
 4. Upload your csv files with domain indicators in **Upload file** input and click on **Next: Review+Create**.
 5. Once validation is successful, click on **Update**.
 6. Follow the same steps to update *TeamCymruScoutIPData* watchlist for ip indicators. 

> **Reference link:** [Bulk update a watchlist](https://learn.microsoft.com/en-us/azure/sentinel/watchlists-manage#bulk-update-a-watchlist)

**STEP 7 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>

**8. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the TeamCymruScout data connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-TeamCymruScout-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the below information : 
		Location 
		WorkspaceName 
		Function Name 
		TeamCymruScoutBaseURL 
		AuthenticationType 
		Username 
		Password 
		APIKey 
		IPValues 
		DomainValues 
		APIType 
		AzureClientId 
		AzureClientSecret 
		TenantId 
		AzureEntraObjectId 
		IPTableName 
		DomainTableName 
		AccountUsageTableName 
		Schedule 
		AccountUsageSchedule 
		LogLevel 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**9. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the TeamCymruScout data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-TeamCymruScout310-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. CymruScoutXXXXX).

	e. **Select a runtime:** Choose Python 3.12 or above.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with their respective values (case-sensitive): 
		CymruScoutBaseURL 
		AuthenticationType 
		TeamCymruScoutUsername 
		TeamCymruScoutPassword 
		APIKey 
		IPValues 
		DomainValues 
		APIType 
		AZURE_CLIENT_ID 
		AZURE_CLIENT_SECRET 
		AZURE_TENANT_ID 
		IPTableName 
		DomainTableName 
		AccountUsageTableName 
		Schedule 
		AccountUsageSchedule 
		LogLevel 
		AZURE_DATA_COLLECTION_ENDPOINT 
		AZURE_DATA_COLLECTION_RULE_ID_MAIN_TABLES 
		AZURE_DATA_COLLECTION_RULE_ID_SUB_TABLES
4. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
