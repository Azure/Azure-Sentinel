# Vectra XDR

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Vectra Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vectra.ai/support](https://www.vectra.ai/support) |
| **Categories** | domains |
| **First Published** | 2023-07-04 |
| **Last Updated** | 2024-08-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Vectra XDR](../connectors/vectraxdr.md)

**Publisher:** Vectra

The [Vectra XDR](https://www.vectra.ai/) connector gives the capability to ingest Vectra Detections, Audits, Entity Scoring, Lockdown, Health and Entities data into Microsoft Sentinel through the Vectra REST API. Refer to the API documentation: `https://support.vectra.ai/s/article/KB-VS-1666` for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **Vectra Client ID** and **Client Secret**  is required for Health, Entity Scoring, Entities, Detections, Lockdown and Audit data collection.  See the documentation to learn more about API on the `https://support.vectra.ai/s/article/KB-VS-1666`.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Vectra API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected. Follow these steps for [Detections Parser](https://aka.ms/sentinel-VectraDetections-parser), [Audits Parser](https://aka.ms/sentinel-VectraAudits-parser), [Entity Scoring Parser](https://aka.ms/sentinel-VectraEntityScoring-parser), [Lockdown Parser](https://aka.ms/sentinel-VectraLockdown-parser) and [Health Parser](https://aka.ms/sentinel-VectraHealth-parser) to create the Kusto functions alias, **VectraDetections**, **VectraAudits**, **VectraEntityScoring**, **VectraLockdown** and **VectraHealth**.

**STEP 1 - Configuration steps for the Vectra API Credentials**

 Follow these instructions to create a Vectra Client ID and Client Secret.
 1. Log into your Vectra portal
 2. Navigate to Manage -> API Clients
 3. From the API Clients page, select 'Add API Client' to create a new client.
 4. Add Client Name, select Role and click on Generate Credentials to obtain your client credentials. 
 5. Be sure to record your Client ID and Secret Key for safekeeping. You will need these two pieces of information to obtain an access token from the Vectra API. An access token is required to make requests to all of the Vectra API endpoints.

**STEP 2 - App Registration steps for the Application in Microsoft Entra ID**

 This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:
 1. Sign in to the [Azure portal](https://portal.azure.com/).
 2. Search for and select **Microsoft Entra ID**.
 3. Under **Manage**, select **App registrations > New registration**.
 4. Enter a display **Name** for your application.
 5. Select **Register** to complete the initial app registration.
 6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the **Application (client) ID** and **Tenant ID**. The client ID and Tenant ID is required as configuration parameters for the execution of Vectra Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)

**STEP 3 - Add a client secret for application in Microsoft Entra ID**

 Sometimes called an application password, a client secret is a string value required for the execution of Vectra Data Connector. Follow the steps in this section to create a new Client Secret:
 1. In the Azure portal, in **App registrations**, select your application.
 2. Select **Certificates & secrets > Client secrets > New client secret**.
 3. Add a description for your client secret.
 4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
 5. Select **Add**. 
 6. *Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page.* The secret value is required as configuration parameter for the execution of Vectra Data Connector. 

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

**STEP 6 - Create a Keyvault**

 Follow these instructions to create a new Keyvault.
 1. In the Azure portal, Go to **Key vaults** and click on Create.
 2. Select Subsciption, Resource Group and provide unique name of keyvault.

**STEP 7 - Create Access Policy in Keyvault**

 Follow these instructions to create access policy in Keyvault.
 1. Go to keyvaults, select your keyvault, go to Access policies on left side panel, click on create.
 2. Select all keys & secrets permissions. Click next.
 3. In the principal section, search by application name which was generated in STEP - 2. Click next.

 **Note: **Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**

**STEP 8 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Vectra data connector, have the Vectra API Authorization Credentials readily available..

**9. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Vectra connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-VectraXDRAPI-azuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-VectraXDRAPI-azuredeploy-gov)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the below information : 
		Function Name 
		Workspace Name 
		Vectra Base URL (https://<vectra-portal-url>) 
		Vectra Client Id - Health 
		Vectra Client Secret Key - Health 
		Vectra Client Id - Entity Scoring 
		Vectra Client Secret - Entity Scoring 
		Vectra Client Id - Detections 
		Vectra Client Secret - Detections 
		Vectra Client Id - Audits 
		Vectra Client Secret - Audits 
		Vectra Client Id - Lockdown 
		Vectra Client Secret - Lockdown 
		Vectra Client Id - Host-Entity 
		Vectra Client Secret - Host-Entity 
		Vectra Client Id - Account-Entity 
		Vectra Client Secret - Account-Entity 
		Key Vault Name 
		Azure Client Id 
		Azure Client Secret 
		Tenant Id 
		Azure Entra ObjectID 
		StartTime (in MM/DD/YYYY HH:MM:SS Format) 
		Include Score Decrease 
		Audits Table Name 
		Detections Table Name 
		Entity Scoring Table Name 
		Lockdown Table Name 
		Health Table Name 
		Entities Table Name 
		Exclude Group Details From Detections
		Log Level (Default: INFO) 
		Lockdown Schedule 
		Health Schedule 
		Detections Schedule 
		Audits Schedule 
		Entity Scoring Schedule 
		Entities Schedule 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**10. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Vectra data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-VectraXDR320-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. VECTRAXXXXX).

	e. **Select a runtime:** Choose Python 3.8 or above.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with their respective values (case-sensitive): 
		Workspace ID 
		Workspace Key 
		Vectra Base URL (https://<vectra-portal-url>) 
		Vectra Client Id - Health 
		Vectra Client Secret Key - Health 
		Vectra Client Id - Entity Scoring 
		Vectra Client Secret - Entity Scoring 
		Vectra Client Id - Detections 
		Vectra Client Secret - Detections 
		Vectra Client Id - Audits 
		Vectra Client Secret - Audits 
		Vectra Client Id - Lockdown 
		Vectra Client Secret - Lockdown 
		Vectra Client Id - Host-Entity 
		Vectra Client Secret - Host-Entity 
		Vectra Client Id - Account-Entity 
		Vectra Client Secret - Account-Entity 
		Key Vault Name 
		Azure Client Id 
		Azure Client Secret 
		Tenant Id 
		StartTime (in MM/DD/YYYY HH:MM:SS Format) 
		Include Score Decrease 
		Audits Table Name 
		Detections Table Name 
		Entity Scoring Table Name 
		Lockdown Table Name 
		Health Table Name 
		Entities Table Name 
		Log Level (Default: INFO) 
		Lockdown Schedule 
		Health Schedule 
		Detections Schedule 
		Audits Schedule 
		Entity Scoring Schedule 
		Entities Schedule 
		logAnalyticsUri (optional) 
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
4. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `Audits_Data_CL` |
| | `Detections_Data_CL` |
| | `Entities_Data_CL` |
| | `Entity_Scoring_Data_CL` |
| | `Health_Data_CL` |
| | `Lockdown_Data_CL` |
| **Connector Definition Files** | [VectraXDR_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Data%20Connectors/VectraDataConnector/VectraXDR_API_FunctionApp.json) |

[→ View full connector details](../connectors/vectraxdr.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Audits_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |
| `Detections_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |
| `Entities_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |
| `Entity_Scoring_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |
| `Health_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |
| `Lockdown_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |

[← Back to Solutions Index](../solutions-index.md)
