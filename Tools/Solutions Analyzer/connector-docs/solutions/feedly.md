# Feedly

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Feedly Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://feedly.com/i/support/contactUs](https://feedly.com/i/support/contactUs) |
| **Categories** | domains |
| **First Published** | 2023-08-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Feedly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Feedly) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Feedly](../connectors/feedly.md)

**Publisher:** Feedly

This connector allows you to ingest IoCs from Feedly.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Azure AD Application Registration**: An Azure AD App Registration with client credentials and permissions to write to the Data Collection Rule. The application must be granted 'Monitoring Metrics Publisher' role on the DCR.
- **Data Collection Endpoint and Rule**: A Data Collection Endpoint (DCE) and Data Collection Rule (DCR) must be created before deploying this connector. [See the documentation to learn more](https://learn.microsoft.com/azure/azure-monitor/logs/custom-logs-migrate).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions and the Logs Ingestion API to pull IoCs from Feedly into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

**1. Step 1 - Prepare Your Environment**

The Feedly connector will automatically create:

- **Custom Table**: `feedly_indicators_CL` with the required schema
- **Data Collection Endpoint (DCE)**: For ingesting data
- **Data Collection Rule (DCR)**: For processing and routing data

No manual resource creation is required - everything will be created during deployment!

For detailed instructions, see: [Migrate from HTTP Data Collector API to Logs Ingestion API](https://learn.microsoft.com/azure/azure-monitor/logs/custom-logs-migrate)

**2. Step 2 - Deploy the Connector**

The ARM template will automatically:

1. Create a managed identity for the Azure Function
2. Assign the **Monitoring Metrics Publisher** role to the Function App on the DCR
3. Configure all necessary permissions for data ingestion

No manual role assignments are required - everything is handled automatically during deployment!

**3. Step 3 - Get your Feedly API token**

Go to https://feedly.com/i/team/api and generate a new API token for the connector.

**4. (Optional Step) Securely store credentials in Azure Key Vault**

Azure Key Vault provides a secure mechanism to store and retrieve secrets. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App by using the `@Microsoft.KeyVault(SecretUri={Security Identifier})` schema.

**5. Step 4 - Deploy the connector**

Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function

>**IMPORTANT:** Before deploying, gather the following information:
- Feedly API Token and Stream IDs

All Azure Monitor resources (DCE, DCR, custom table, and role assignments) will be created automatically during deployment.
**Option 1 - Azure Resource Manager (ARM) Template**

  Use this method for automated deployment of the Feedly connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-Feedly-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the required parameters:
   - **TableName**: Name for the custom table (default: `feedly_indicators_CL`)
   - **FeedlyApiKey**: Your Feedly API token from Step 3
   - **FeedlyStreamIds**: Comma-separated list of Feedly stream IDs
   - **DaysToBackfill**: Number of days to backfill (default: 7)

>**Note**: If using Azure Key Vault secrets, use the `@Microsoft.KeyVault(SecretUri={Security Identifier})` schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the Feedly connector manually with Azure Functions (Deployment via Visual Studio Code).
**1. Deploy a Function App**

    **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://github.com/Azure/Azure-Sentinel/raw/refs/heads/master/Solutions/Feedly/Data%20Connectors/FeedlyAzureFunction.zip) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity Bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. FeedlyXXXX).

	e. **Select a runtime:** Choose Python 3.10.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

    **2. Configure the Function App**

    1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **New application setting**.
3. Add each of the following application settings individually, with their respective values (case-sensitive):
		- `DataCollectionEndpoint`: Will be populated automatically after DCE creation
		- `DcrImmutableId`: Will be populated automatically after DCR creation
		- `DcrStreamName`: `feedly_indicators_CL`
		- `FeedlyApiKey`: Your Feedly API token
		- `FeedlyStreamIds`: Comma-separated Feedly stream IDs
		- `DaysToBackfill`: Number of days to backfill (e.g., 7)

**Note**: The Function App uses managed identity for authentication to Azure Monitor, so no Azure AD credentials are needed.

>**Note**: Use Azure Key Vault references for sensitive values: `@Microsoft.KeyVault(SecretUri={Security Identifier})`

4. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `feedly_indicators_CL` |
| **Connector Definition Files** | [Feedly_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Feedly/Data%20Connectors/Feedly_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/feedly.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `feedly_indicators_CL` | [Feedly](../connectors/feedly.md) |

[← Back to Solutions Index](../solutions-index.md)
