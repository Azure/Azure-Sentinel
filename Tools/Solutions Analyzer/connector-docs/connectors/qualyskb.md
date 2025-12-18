# Qualys VM KnowledgeBase

| | |
|----------|-------|
| **Connector ID** | `QualysKB` |
| **Publisher** | Qualys |
| **Tables Ingested** | [`QualysKB_CL`](../tables-index.md#qualyskb_cl) |
| **Used in Solutions** | [Qualys VM Knowledgebase](../solutions/qualys-vm-knowledgebase.md) |
| **Connector Definition Files** | [QualysKB_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Qualys%20VM%20Knowledgebase/Data%20Connectors/QualysKB_API_FunctionApp.json) |

The [Qualys Vulnerability Management (VM)](https://www.qualys.com/apps/vulnerability-management/) KnowledgeBase (KB) connector provides the capability to ingest the latest vulnerability data from the Qualys KB into Microsoft Sentinel. 



 This data can used to correlate and enrich vulnerability detections found by the [Qualys Vulnerability Management (VM)](https://docs.microsoft.com/azure/sentinel/connect-qualys-vm) data connector.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Qualys API Key**: A Qualys VM API username and password is required. [See the documentation to learn more about Qualys VM API](https://www.qualys.com/docs/qualys-api-vmpc-user-guide.pdf).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias QualysVM Knowledgebase and load the function code or click [here](https://aka.ms/sentinel-crowdstrikefalconendpointprotection-parser), on the second line of the query, enter the hostname(s) of your QualysVM Knowledgebase device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

>This data connector depends on a parser based on a Kusto Function to work as expected. [Follow the steps](https://aka.ms/sentinel-qualyskb-parser) to use the Kusto function alias, **QualysKB**

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Configuration steps for the Qualys API**

1. Log into the Qualys Vulnerability Management console with an administrator account, select the **Users** tab and the **Users** subtab. 
2. Click on the **New** drop-down menu and select **Users**.
3. Create a username and password for the API account. 
4. In the **User Roles** tab, ensure the account role is set to **Manager** and access is allowed to **GUI** and **API**
4. Log out of the administrator account and log into the console with the new API credentials for validation, then log out of the API account. 
5. Log back into the console using an administrator account and modify the API accounts User Roles, removing access to **GUI**. 
6. Save all changes.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Qualys KB connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Qualys API username and password, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the Qualys KB connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-qualyskb-azuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-qualyskb-azuredeploy-gov)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **API Username**, **API Password** , update the **URI**, and any additional URI **Filter Parameters** (This value should include a "&" symbol between each parameter and should not include any spaces) 
> - Enter the URI that corresponds to your region. The complete list of API Server URLs can be [found here](https://www.qualys.com/docs/qualys-api-vmpc-user-guide.pdf#G4.735348)
> - Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.
 - Note: If deployment failed due to the storage account name being taken, change the **Function Name** to a unique value and redeploy.

  **Option 2 - Manual Deployment of Azure Functions**

  This method provides the step-by-step instructions to deploy the Qualys KB connector manually with Azure Function.
**Step 1 - Deploy a Function App**

    1. Download the [Azure Function App](https://aka.ms/sentinel-qualyskb-functioncode) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Configuration**.
3. In the **Application settings** tab, select **+ New application setting**.
4. Add each of the following seven (7) application settings individually, with their respective string values (case-sensitive): 
		apiUsername
		apiPassword
		workspaceID
		workspaceKey
		uri
		filterParameters
		logAnalyticsUri (optional)
> - Enter the URI that corresponds to your region. The complete list of API Server URLs can be [found here](https://www.qualys.com/docs/qualys-api-vmpc-user-guide.pdf#G4.735348). The `uri` value must follow the following schema: `https://<API Server>/api/2.0` 
> - Add any additional filter parameters, for the `filterParameters` variable, that need to be appended to the URI. The `filterParameter` value should include a "&" symbol between each parameter and should not include any spaces.
> - Note: If using Azure Key Vault, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details.
 - Use logAnalyticsUri to override the log analytics API endpoint for delegated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
5. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
