# Digital Shadows

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Digital Shadows |
| **Support Tier** | Partner |
| **Support Link** | [https://www.digitalshadows.com/](https://www.digitalshadows.com/) |
| **Categories** | domains |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Digital Shadows Searchlight](../connectors/digitalshadowssearchlightazurefunctions.md)

**Publisher:** Digital Shadows

The Digital Shadows data connector provides ingestion of the incidents and alerts from Digital Shadows Searchlight into the Microsoft Sentinel using the REST API. The connector will provide the incidents and alerts information such that it helps to examine, diagnose and analyse the potential security risks and threats.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **Digital Shadows account ID, secret and key** is required.  See the documentation to learn more about API on the `https://portal-digitalshadows.com/learn/searchlight-api/overview/description`.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to a 'Digital Shadows Searchlight' to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Configuration steps for the 'Digital Shadows Searchlight' API**

The provider should provide or link to detailed steps to configure the 'Digital Shadows Searchlight' API endpoint so that the Azure Function can authenticate to it successfully, get its authorization key or token, and pull the appliance's logs into Microsoft Sentinel.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the 'Digital Shadows Searchlight' connector, have the Workspace ID  and Workspace Primary Key (can be copied from the following), as well as the 'Digital Shadows Searchlight' API authorization key(s) or Token, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the 'Digital Shadows Searchlight' connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-Digitalshadows-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **API Username**, **API Password**, 'and/or Other required fields'. 
>Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**Option 2 - Manual Deployment of Azure Functions**

 Use the following step-by-step instructions to deploy the 'Digital Shadows Searchlight' connector manually with Azure Functions.

**1. Create a Function App**

1.  From the Azure Portal, navigate to [Function App](https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites/kind/functionapp).
2. Click **+ Create** at the top.
3. In the **Basics** tab, ensure Runtime stack is set to **python 3.11**. 
4. In the **Hosting** tab, ensure **Plan type** is set to **'Consumption (Serverless)'**.
5.select Storage account
6. 'Add other required configurations'. 
5. 'Make other preferable configuration changes', if needed, then click **Create**.

**2. Import Function App Code(Zip deployment)**

1. Install Azure CLI
2. From terminal type **az functionapp deployment source config-zip -g <ResourceGroup> -n <FunctionApp> --src <Zip File>** and hit enter. Set the `ResourceGroup` value to: your resource group name. Set the `FunctionApp` value to: your newly created function app name. Set the `Zip File` value to: `digitalshadowsConnector.zip`(path to your zip file). Note:- Download the zip file from the link - [Function App Code](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows/Data%20Connectors/Digital%20Shadows/digitalshadowsConnector.zip)

**3. Configure the Function App**

1. In the Function App screen, click the Function App name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following 'x (number of)' application settings individually, under Name, with their respective string values (case-sensitive) under Value: 
		DigitalShadowsAccountID
		WorkspaceID
		WorkspaceKey
		DigitalShadowsKey
		DigitalShadowsSecret
		HistoricalDays
		DigitalShadowsURL
		ClassificationFilterOperation
		HighVariabilityClassifications
		FUNCTION_NAME
		logAnalyticsUri (optional)
(add any other settings required by the Function App)
Set the `DigitalShadowsURL` value to: `https://api.searchlight.app/v1`
Set the `HighVariabilityClassifications` value to: `exposed-credential,marked-document`
Set the `ClassificationFilterOperation` value to: `exclude` for exclude function app or `include` for include function app 
>Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Azure Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details.
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: https://<CustomerId>.ods.opinsights.azure.us. 
4. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `DigitalShadows_CL` |
| **Connector Definition Files** | [DigitalShadowsSearchlight_API_functionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows/Data%20Connectors/Digital%20Shadows/DigitalShadowsSearchlight_API_functionApp.json) |

[→ View full connector details](../connectors/digitalshadowssearchlightazurefunctions.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DigitalShadows_CL` | [Digital Shadows Searchlight](../connectors/digitalshadowssearchlightazurefunctions.md) |

[← Back to Solutions Index](../solutions-index.md)
