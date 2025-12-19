# Agari

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Agari |
| **Support Tier** | Partner |
| **Support Link** | [https://support.agari.com/hc/en-us/articles/360000645632-How-to-access-Agari-Support](https://support.agari.com/hc/en-us/articles/360000645632-How-to-access-Agari-Support) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Agari](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Agari) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Agari Phishing Defense and Brand Protection](../connectors/agari.md)

**Publisher:** Agari

This connector uses a Agari REST API connection to push data into Azure Sentinel Log Analytics.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Agari Phishing Defense, Phishing Response or Brand Protection API Client ID and Secret**: Ensure you have your Client ID and Secret keys. Instructions can be found on the [Agari Developers Site](https://developers.agari.com/agari-platform/docs/quick-start).
- **(Optional) Microsoft Security Graph API**: The Agari Function App has the ability to share threat intelleigence with Sentinel via the Security Graph API. To use this feature, you will need to enable the [Sentinel Threat Intelligence Platforms connector](https://docs.microsoft.com/azure/sentinel/connect-threat-intelligence) as well as register an application in Azure Active Directory.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Agari APIs to pull its logs into Azure Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**1. STEP 1 - Get your Agari API credentials**

1. Log into any Agari product (Client ID and Secret are the same for all applications) 
2. Click on your username in the upper right and select **Settings**
3. Click on the **Generate API Secret** link to generate an API client_id and client_secret (the link will read **Regenerate API Secret** if you have already generated an API client ID/secret previously)
4. Copy both the client_id and client_secret that are generated

**2. STEP 2 - (Optional) Enable the Security Graph API**

Follow the instrcutions found on article [Connect Azure Sentinel to your threat intelligence platform](https://docs.microsoft.com/azure/sentinel/connect-threat-intelligence#connect-azure-sentinel-to-your-threat-intelligence-platform). Once the application is created you will need to record the Tenant ID, Client ID and Client Secret.

**3. STEP 3 - Deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Agari Connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Agari API credentials from the previous step.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**4. Choose a deployement option**

**5. Option 1: Deploy using the Azure Resource Manager (ARM) Template**

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-agari-azuredeploy) 
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **Agari Client ID**, **Agari Client Secret**, select `True` or `False` for the products you subscribe to, and if you wish to share IoCs with Sentinel, select `True` For **Enable Security Graph Sharing**, and enter the required IDs from the Azure Application.
> - The Function App will request data from the Agari APIs every 5 minutes, corresponding to the Funciton App Timer.
> - Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.
6. **NOTE:** Due to the use of Environment Variables to store log access times, the App requires 1 additonal manual step. In the Function App, select the Function App Name and select Click on **Identity** and for System assigned Identity, click on **Azure role assignments** and **Add Role assignment**. Select **Subscription** as the scope, select your subscription and set the Role to **Contributor**. Click on **Save**.

**6. Option 2: Manual Deployment of Azure Functions**

**1. Create a Function App**

1.  From the Azure Portal, navigate to [Function App](https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites/kind/functionapp), and select **+ Add**.
2. In the **Basics** tab, ensure Runtime stack is set to **Powershell Core**. 
3. In the **Hosting** tab, ensure the **Consumption (Serverless)** plan type is selected.
4. Make other preferrable configuration changes, if needed, then click **Create**.

**2. Import Function App Code**

1. In the newly created Function App, select **Functions** on the left pane and click **+ Add**.
2. Click on **Code + Test** on the left pane. 
3. Copy the [Function App Code](https://aka.ms/sentinel-agari-functionapp) and paste into the Function App `run.ps1` editor.
3. Click **Save**.

**3. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following eight to twelve (8-12) application settings individually, with their respective string values (case-sensitive): 
		clientID
		clientSecret
		workspaceID
		workspaceKey
		enableBrandProtectionAPI
		enablePhishingResponseAPI
		enablePhishingDefenseAPI
		resGroup
		functionName
		subId
		enableSecurityGraphSharing
		<--- Required if enableSecurityGraphSharing is set to true --->
		GraphTenantId
		GraphClientId
		GraphClientSecret
		logAnalyticsUri (optional)
> - Enter your Agari ClientID and Secret in 'clientId' and 'clientSecret'
> - Enter 'true' or 'false' for 'enablePhishingDefense', 'enableBrandProtection', 'enablePhishingResponse' as per your product subscriptions.
> - Enter your Resource Group name in resGroup, the name of the Function (from previous step) in functionName and your Subscription ID in subId.
> - Enter 'true' or 'false' for 'enableSecurtyGraphAPI'. If you are enabling the Security Graph, the 'GraphTenantId','GraphClientId', and 'GraphClientSecret' is required.
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.

**4. Set Permissions for the App**

1. In the Function App, select the Function App Name and select Click on **Identity** and for System assigned Identity, set the status to On. 

2. Next, click on **Azure role assignments** and **Add Role assignment**. Select **Subscription** as the scope, select your subscription and set the Role to **Contributor**. Click on **Save**.

**5. Complete Setup.**

1. Once all application settings have been entered, click **Save**. Note that it will take some time to have the required dependencies download, so you may see some inital failure messages.

| | |
|--------------------------|---|
| **Tables Ingested** | `agari_apdpolicy_log_CL` |
| | `agari_apdtc_log_CL` |
| | `agari_bpalerts_log_CL` |
| **Connector Definition Files** | [Agari_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Agari/Data%20Connectors/Agari_API_FunctionApp.json) |

[→ View full connector details](../connectors/agari.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `agari_apdpolicy_log_CL` | [Agari Phishing Defense and Brand Protection](../connectors/agari.md) |
| `agari_apdtc_log_CL` | [Agari Phishing Defense and Brand Protection](../connectors/agari.md) |
| `agari_bpalerts_log_CL` | [Agari Phishing Defense and Brand Protection](../connectors/agari.md) |

[← Back to Solutions Index](../solutions-index.md)
