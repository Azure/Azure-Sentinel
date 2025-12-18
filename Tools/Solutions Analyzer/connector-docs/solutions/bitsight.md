# BitSight

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | BitSight Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.bitsight.com/customer-success-support](https://www.bitsight.com/customer-success-support) |
| **Categories** | domains |
| **First Published** | 2023-02-20 |
| **Last Updated** | 2024-02-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Bitsight data connector](../connectors/bitsight.md)

**Publisher:** BitSight Technologies, Inc.

The [BitSight](https://www.BitSight.com/) Data Connector supports evidence-based cyber risk monitoring by bringing BitSight data in Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: BitSight API Token is required.  See the documentation to [learn more](https://help.bitsighttech.com/hc/en-us/articles/115014888388-API-Token-Management) about API Token.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the BitSight API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Steps to Create/Get Bitsight API Token**

 Follow these instructions to get a BitSight API Token.
 1. For SPM App: Refer to the [User Preference](https://service.bitsight.com/app/spm/account) tab of your Account page, 
		Go to Settings > Account > User Preferences > API Token.
 2. For TPRM App: Refer to the [User Preference](https://service.bitsight.com/app/tprm/account) tab of your Account page, 
		Go to Settings > Account > User Preferences > API Token.
 3. For Classic BitSight: Go to your [Account](https://service.bitsight.com/settings) page, 
		Go to Settings > Account > API Token.

**STEP 2 - App Registration steps for the Application in Microsoft Entra ID**

 This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:
 1. Sign in to the [Azure portal](https://portal.azure.com/).
 2. Search for and select **Microsoft Entra ID**.
 3. Under **Manage**, select **App registrations > New registration**.
 4. Enter a display **Name** for your application.
 5. Select **Register** to complete the initial app registration.
 6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the **Application (client) ID** and **Tenant ID**. The client ID and Tenant ID is required as configuration parameters for the execution of BitSight Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)

**STEP 3 - Add a client secret for application in Microsoft Entra ID**

 Sometimes called an application password, a client secret is a string value required for the execution of BitSight Data Connector. Follow the steps in this section to create a new Client Secret:
 1. In the Azure portal, in **App registrations**, select your application.
 2. Select **Certificates & secrets > Client secrets > New client secret**.
 3. Add a description for your client secret.
 4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
 5. Select **Add**. 
 6. *Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page.* The secret value is required as configuration parameter for the execution of BitSight Data Connector. 

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

**STEP 6 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the BitSight data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following) readily available.., as well as the BitSight API Token.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**7. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the BitSight connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-BitSight-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the below information :  

	 a. **FunctionName** - Name of the Azure Function App to be created. Default is BitSight. 

	 b. **API_token** - Enter API Token of your BitSight account. 

	 c. **Azure_Client_Id** - Enter Azure Client Id that you have created during app registration. 

	 d. **Azure_Client_Secret** - Enter Azure Client Secret that you have created during creating the client secret. 

	 e. **Azure_Tenant_Id** - Enter Azure Tenant Id of your Microsoft Entra ID. 

	 f. **Azure_Entra_Object_Id** - Enter Object id of your Microsoft Entra App. 

	 g. **Companies** - Please add valid company names separated by asterisk(*). For example: Actors Films*Goliath Investments LLC*HCL Group*Saperix, Inc. 

	 h. **Location** - The location in which the data collection rules and data collection endpoints should be deployed. 

	 i. **WorkspaceName** - Log analytics workspace name. Can be found under Log analytics "Settings". 

	 j. **Portfolio_Companies_Table_Name** - Name of the table to store portfolio companies. Default is BitsightPortfolio_Companies. Please do not keep this field as empty else you will get validation error. 

	 k. **Alerts_Table_Name** - Name of the table to store alerts. Default is BitsightAlerts_data. Please do not keep this field as empty else you will get validation error. 

	 l. **Breaches_Table_Name** - Name of the table to store breaches. Default is BitsightBreaches_data. Please do not keep this field as empty else you will get validation error. 

	 m. **Company_Table_Name** - Name of the table to store company details. Default is BitsightCompany_details. Please do not keep this field as empty else you will get validation error. 

	 n. **Company_Rating_Details_Table_Name** - Name of the table to store company rating details. Default is BitsightCompany_rating_details. Please do not keep this field as empty else you will get validation error. 

	 o. **Diligence_Historical_Statistics_Table_Name** - Name of the table to store diligence historical statistics. Default is BitsightDiligence_historical_statistics. Please do not keep this field as empty else you will get validation error. 

	 p. **Diligence_Statistics_Table_Name** - Name of the table to store diligence statistics. Default is BitsightDiligence_statistics. Please do not keep this field as empty else you will get validation error. 

	 q. **Findings_Summary_Table_Name** - Name of the table to store findings summary. Default is BitsightFindings_summary. Please do not keep this field as empty else you will get validation error. 

	 r. **Findings_Table_Name** - Name of the table to store findings data. Default is BitsightFindings_data. Please do not keep this field as empty else you will get validation error. 

	 s. **Graph_Table_Name** - Name of the table to store graph data. Default is BitsightGraph_data. Please do not keep this field as empty else you will get validation error. 

	 t. **Industrial_Statistics_Table_Name** - Name of the table to store industrial statistics. Default is BitsightIndustrial_statistics. Please do not keep this field as empty else you will get validation error. 

	 u. **Observation_Statistics_Table_Name** - Name of the table to store observation statistics. Default is BitsightObservation_statistics. Please do not keep this field as empty else you will get validation error. 

	 v. **LogLevel** - Select log level or log severity value from DEBUG, INFO, ERROR. By default it is set to INFO. 

	 w. **Schedule** - Please enter a valid Quartz cron-expression. (Example: 0 0 * * * *). 

	 x. **Schedule_Portfolio** - Please enter a valid Quartz cron-expression. (Example: 0 */30 * * * *). 

	 y. **AppInsightsWorkspaceResourceID** - Use 'Log Analytic Workspace-->Properties' blade having 'Resource ID' property value. This is a fully qualified resourceId which is in format '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}'. 
4. Once all application settings have been entered, click **Review + create** to deploy..

**8. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the BitSight data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-BitSight310-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. BitSightXXXXX).

	e. **Select a runtime:** Choose Python 3.8 or above.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with their respective values (case-sensitive): 

	 a. **FunctionName** - Name of the Azure Function App to be created. Default is BitSight. 

	 b. **API_token** - Enter API Token of your BitSight account. 

	 c. **Azure_Client_Id** - Enter Azure Client Id that you have created during app registration. 

	 d. **Azure_Client_Secret** - Enter Azure Client Secret that you have created during creating the client secret. 

	 e. **Azure_Tenant_Id** - Enter Azure Tenant Id of your Microsoft Entra ID. 

	 f. **Azure_Entra_Object_Id** - Enter Object id of your Microsoft Entra App. 

	 g. **Companies** - Please add valid company names separated by asterisk(*). For example: Actors Films*Goliath Investments LLC*HCL Group*Saperix, Inc. 

	 h. **Location** - The location in which the data collection rules and data collection endpoints should be deployed. 

	 i. **WorkspaceName** - Log analytics workspace name. Can be found under Log analytics "Settings". 

	 j. **Portfolio_Companies_Table_Name** - Name of the table to store portfolio companies. Default is BitsightPortfolio_Companies. Please do not keep this field as empty else you will get validation error. 

	 k. **Alerts_Table_Name** - Name of the table to store alerts. Default is BitsightAlerts_data. Please do not keep this field as empty else you will get validation error. 

	 l. **Breaches_Table_Name** - Name of the table to store breaches. Default is BitsightBreaches_data. Please do not keep this field as empty else you will get validation error. 

	 m. **Company_Table_Name** - Name of the table to store company details. Default is BitsightCompany_details. Please do not keep this field as empty else you will get validation error. 

	 n. **Company_Rating_Details_Table_Name** - Name of the table to store company rating details. Default is BitsightCompany_rating_details. Please do not keep this field as empty else you will get validation error. 

	 o. **Diligence_Historical_Statistics_Table_Name** - Name of the table to store diligence historical statistics. Default is BitsightDiligence_historical_statistics. Please do not keep this field as empty else you will get validation error. 

	 p. **Diligence_Statistics_Table_Name** - Name of the table to store diligence statistics. Default is BitsightDiligence_statistics. Please do not keep this field as empty else you will get validation error. 

	 q. **Findings_Summary_Table_Name** - Name of the table to store findings summary. Default is BitsightFindings_summary. Please do not keep this field as empty else you will get validation error. 

	 r. **Findings_Table_Name** - Name of the table to store findings data. Default is BitsightFindings_data. Please do not keep this field as empty else you will get validation error. 

	 s. **Graph_Table_Name** - Name of the table to store graph data. Default is BitsightGraph_data. Please do not keep this field as empty else you will get validation error. 

	 t. **Industrial_Statistics_Table_Name** - Name of the table to store industrial statistics. Default is BitsightIndustrial_statistics. Please do not keep this field as empty else you will get validation error. 

	 u. **Observation_Statistics_Table_Name** - Name of the table to store observation statistics. Default is BitsightObservation_statistics. Please do not keep this field as empty else you will get validation error. 

	 v. **LogLevel** - Select log level or log severity value from DEBUG, INFO, ERROR. By default it is set to INFO. 

	 w. **Schedule** - Please enter a valid Quartz cron-expression. (Example: 0 0 * * * *). 

	 x. **Schedule_Portfolio** - Please enter a valid Quartz cron-expression. (Example: 0 */30 * * * *). 

	 y. **AppInsightsWorkspaceResourceID** - Use 'Log Analytic Workspace-->Properties' blade having 'Resource ID' property value. This is a fully qualified resourceId which is in format '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}'. 
4. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `BitsightAlerts_data_CL` |
| | `BitsightBreaches_data_CL` |
| | `BitsightCompany_details_CL` |
| | `BitsightCompany_rating_details_CL` |
| | `BitsightDiligence_historical_statistics_CL` |
| | `BitsightDiligence_statistics_CL` |
| | `BitsightFindings_data_CL` |
| | `BitsightFindings_summary_CL` |
| | `BitsightGraph_data_CL` |
| | `BitsightIndustrial_statistics_CL` |
| | `BitsightObservation_statistics_CL` |
| **Connector Definition Files** | [BitSight_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BitSight/Data%20Connectors/BitSightDataConnector/BitSight_API_FunctionApp.json) |

[→ View full connector details](../connectors/bitsight.md)

## Tables Reference

This solution ingests data into **11 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BitsightAlerts_data_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightBreaches_data_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightCompany_details_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightCompany_rating_details_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightDiligence_historical_statistics_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightDiligence_statistics_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightFindings_data_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightFindings_summary_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightGraph_data_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightIndustrial_statistics_CL` | [Bitsight data connector](../connectors/bitsight.md) |
| `BitsightObservation_statistics_CL` | [Bitsight data connector](../connectors/bitsight.md) |

[← Back to Solutions Index](../solutions-index.md)
