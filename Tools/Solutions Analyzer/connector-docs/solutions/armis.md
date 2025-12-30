# Armis

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Armis Corporation |
| **Support Tier** | Partner |
| **Support Link** | [https://support.armis.com/](https://support.armis.com/) |
| **Categories** | domains |
| **First Published** | 2022-08-02 |
| **Last Updated** | 2024-08-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis) |

## Data Connectors

This solution provides **4 data connector(s)**.

### [Armis Activities](../connectors/armisactivities.md)

**Publisher:** Armis

### [Armis Alerts](../connectors/armisalerts.md)

**Publisher:** Armis

### [Armis Alerts Activities](../connectors/armisalertsactivities.md)

**Publisher:** Armis

### [Armis Devices](../connectors/armisdevices.md)

**Publisher:** Armis

The [Armis](https://www.armis.com/) Device connector gives the capability to ingest Armis Devices into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get device information from the Armis platform. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. Armis can also integrate with your existing IT & security management tools to identify and classify each and every device, managed or unmanaged in your environment.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **Armis Secret Key** is required.  See the documentation to learn more about API on the `https://<YourArmisInstance>.armis.com/api/v1/doc`

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Armis API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected. [Follow these steps](https://aka.ms/sentinel-ArmisDevice-parser) to create the Kusto functions alias, **ArmisDevice**

**STEP 1 - Configuration steps for the Armis API**

 Follow these instructions to create an Armis API secret key.
 1. Log into your Armis instance
 2. Navigate to Settings -> API Management
 3. If the secret key has not already been created, press the Create button to create the secret key
 4. To access the secret key, press the Show button
 5. The secret key can now be copied and used during the Armis Device connector configuration

**STEP 2 - App Registration steps for the Application in Microsoft Entra ID**

 This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:
 1. Sign in to the [Azure portal](https://portal.azure.com/).
 2. Search for and select **Microsoft Entra ID**.
 3. Under **Manage**, select **App registrations > New registration**.
 4. Enter a display **Name** for your application.
 5. Select **Register** to complete the initial app registration.
 6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the **Application (client) ID** and **Tenant ID**. The client ID and Tenant ID is required as configuration parameters for the execution of Armis Device Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)

**STEP 3 - Add a client secret for application in Microsoft Entra ID**

 Sometimes called an application password, a client secret is a string value required for the execution of Armis Device Data Connector. Follow the steps in this section to create a new Client Secret:
 1. In the Azure portal, in **App registrations**, select your application.
 2. Select **Certificates & secrets > Client secrets > New client secret**.
 3. Add a description for your client secret.
 4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
 5. Select **Add**. 
 6. *Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page.* The secret value is required as configuration parameter for the execution of Armis Device Data Connector. 

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
 1. In the Azure portal, Go to **Key vaults**. Click create.
 2. Select Subsciption, Resource Group and provide unique name of keyvault.

> **NOTE:** Create a separate key vault for each **API key** within one workspace.

**STEP 7 - Create Access Policy in Keyvault**

 Follow these instructions to create access policy in Keyvault.
 1. Go to keyvaults, select your keyvault, go to Access policies on left side panel. Click create.
 2. Select all keys & secrets permissions. Click next.
 3. In the principal section, search by application name which was generated in STEP - 2. Click next.

> **NOTE:** Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**

**STEP 8 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Armis Device data connector, have the Armis API Authorization Key(s) readily available..

**9. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Armis connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ArmisDevice-azuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-ArmisDevice-azuredeploy-gov)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the below information : 
		Function Name 
		Location 
		Workspace Name 
		Armis Secret Key 
		Armis URL (https://<armis-instance>.armis.com/api/v1/) 
		Armis Device Table Name 
		Armis Schedule 
		KeyVault Name 
		Azure Client Id 
		Azure Client Secret 
		Azure Entra ObjectID 
		Tenant Id 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**10. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Armis Device data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-ArmisDevice320-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. ARMISXXXXX).

	e. **Select a runtime:** Choose Python 3.12

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with their respective values (case-sensitive): 
		Location 
		Workspace Name 
		Armis Secret Key 
		Armis URL (https://<armis-instance>.armis.com/api/v1/) 
		Armis Device Table Name 
		Armis Schedule 
		KeyVault Name 
		Azure Client Id 
		Azure Client Secret 
		Azure Entra ObjectID 
		Tenant Id 
		logAnalyticsUri (optional) 
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
4. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `Armis_Devices_CL` |
| **Connector Definition Files** | [ArmisDevice_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisDevice/ArmisDevice_API_FunctionApp.json) |

[→ View full connector details](../connectors/armisdevices.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Armis_Activities_CL` | [Armis Activities](../connectors/armisactivities.md), [Armis Alerts Activities](../connectors/armisalertsactivities.md) |
| `Armis_Alerts_CL` | [Armis Alerts](../connectors/armisalerts.md), [Armis Alerts Activities](../connectors/armisalertsactivities.md) |
| `Armis_Devices_CL` | [Armis Devices](../connectors/armisdevices.md) |

[← Back to Solutions Index](../solutions-index.md)
