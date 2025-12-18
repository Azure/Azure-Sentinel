# SecurityScorecard Cybersecurity Ratings

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | SecurityScorecard |
| **Support Tier** | Partner |
| **Support Link** | [https://support.securityscorecard.com/hc/en-us/requests/new](https://support.securityscorecard.com/hc/en-us/requests/new) |
| **Categories** | domains |
| **First Published** | 2022-10-01 |
| **Last Updated** | 2022-10-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityScorecard%20Cybersecurity%20Ratings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityScorecard%20Cybersecurity%20Ratings) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [SecurityScorecard Factor](../connectors/securityscorecardfactorazurefunctions.md)

**Publisher:** SecurityScorecard

### [SecurityScorecard Issue](../connectors/securityscorecardissueazurefunctions.md)

**Publisher:** SecurityScorecard

### [SecurityScorecard Cybersecurity Ratings](../connectors/securityscorecardratingsazurefunctions.md)

**Publisher:** SecurityScorecard

SecurityScorecard is the leader in cybersecurity risk ratings. The [SecurityScorecard](https://www.SecurityScorecard.com/) data connector provides the ability for Sentinel to import SecurityScorecard ratings as logs. SecurityScorecard provides ratings for over 12 million companies and domains using countless data points from across the internet. Maintain full awareness of any company's security posture and be able to receive timely updates when scores change or drop. SecurityScorecard ratings are updated daily based on evidence collected across the web.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **SecurityScorecard API Key** is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the SecurityScorecard API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Configuration steps for the SecurityScorecard API**

 Follow these instructions to create/get a SecurityScorecard API token.
 1. As an administrator in SecurityScorecard, navigate to My Settings and then Users
 2. Click '+ Add User'
 3. In the form, check off 'Check to create a bot user'
 4. Provide a name for the Bot and provide it with Read Only permission
 5. Click 'Add User'
 6. Locate the newly created Bot user
 7. Click 'create token' in the Bot user's row
 8. Click 'Confirm' and note the API token that has been generated

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the SecurityScorecard Ratings data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following) readily available.., as well as the SecurityScorecard API Authorization Key(s)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the SecurityScorecard Ratings connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-SecurityScorecardRatingsAPI-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the below information : 
		Function Name 
		Workspace ID 
		Workspace Key 
		SecurityScorecard API Key 
		SecurityScorecard Base URL (https://api.securityscorecard.io) 
		Domain 
		Portfolio IDs (Coma separated IDs) 
		SecurityScorecard Ratings Table Name (Default: SecurityScorecardRatings) 
		Level Ratings Change (Default: 7) 
		Ratings Schedule (Default: 0 45 * * * *) 
		Diff Override Own Ratings (Default: true) 
		Diff Override Portfolio Ratings (Default: true) 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the SecurityScorecard Ratings data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-SecurityScorecardRatingsAPI-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. SecurityScorecardXXXXX).

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
		SecurityScorecard API Key 
		SecurityScorecard Base URL (https://api.securityscorecard.io) 
		Domain 
		Portfolio IDs (Coma separated IDs) 
		SecurityScorecard Ratings Table Name (Default: SecurityScorecardRatings) 
		Level Ratings Change (Default: 7) 
		Ratings Schedule (Default: 0 45 * * * *) 
		Diff Override Own Ratings (Default: true) 
		Diff Override Portfolio Ratings (Default: true) 
		logAnalyticsUri (optional) 
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
4. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `SecurityScorecardRatings_CL` |
| **Connector Definition Files** | [SecurityScorecardRatings_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityScorecard%20Cybersecurity%20Ratings/Data%20Connectors/SecurityScorecardRatings/SecurityScorecardRatings_API_FunctionApp.json) |

[→ View full connector details](../connectors/securityscorecardratingsazurefunctions.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityScorecardFactor_CL` | [SecurityScorecard Factor](../connectors/securityscorecardfactorazurefunctions.md) |
| `SecurityScorecardIssues_CL` | [SecurityScorecard Issue](../connectors/securityscorecardissueazurefunctions.md) |
| `SecurityScorecardRatings_CL` | [SecurityScorecard Cybersecurity Ratings](../connectors/securityscorecardratingsazurefunctions.md) |

[← Back to Solutions Index](../solutions-index.md)
