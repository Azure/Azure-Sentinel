# CyberArkAudit

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | CyberArk Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyberark.com/services-support/technical-support-contact/](https://www.cyberark.com/services-support/technical-support-contact/) |
| **Categories** | domains |
| **First Published** | 2024-03-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CyberArkAudit](../connectors/cyberarkaudit.md)

**Publisher:** CyberArk

The [CyberArk Audit](https://docs.cyberark.com/Audit/Latest/en/Content/Resources/_TopNav/cc_Home.htm) data connector provides the capability to retrieve security event logs of the CyberArk Audit service and more events into Microsoft Sentinel through the REST API. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Audit REST API Connections details and Credentials**: **OauthUsername**, **OauthPassword**, **WebAppID**, **AuditApiKey**, **IdentityEndpoint** and **AuditApiBaseUrl** are required for making API calls.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Azure Blob Storage API to pull logs into Microsoft Sentinel. This might result in additional costs for data ingestion and for storing data in Azure Blob Storage costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) and [Azure Blob Storage pricing page](https://azure.microsoft.com/pricing/details/storage/blobs/) for details.

>**NOTE:** API authorization key(s) or token(s) are securely stored in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values.

**STEP 1 - Configuration steps for the CyberArk Audit SIEM Integration**

 Follow the [instructions](https://docs.cyberark.com/audit/latest/en/Content/Audit/isp_Microsoft_Sentinel.htm?tocpath=SIEM%20integrations%7C_____3) to obtain connection details and credentials.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the CyberArk Audit data connector, have the Workspace Name and Workspace Location (can be copied from the following).
- **Workspace Name**: `WorkspaceName`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Workspace Location**: `WorkspaceLocation`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the CyberArk Audit data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-CyberArkAuditAPI-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
> **NOTE:** Within the same resource group, you can't mix Windows and Linux apps in the same region. Select existing resource group without Windows apps in it or create new resource group.
3. Enter the **CyberArkAuditUsername**, **CyberArkAuditPassword**, **CyberArkAuditServerURL**  and deploy. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the CyberArk Audit data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-CyberArkAudit-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. CyberArkXXXXX).

	e. **Select a runtime:** Choose Python 3.10.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select ** New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		CyberArkAuditUsername
		CyberArkAuditPassword
		CyberArkAuditServerURL
		WorkspaceID
		WorkspaceKey
		logAnalyticsUri (optional)
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
4. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `CyberArkAudit` |
| | `CyberArk_AuditEvents_CL` |
| **Connector Definition Files** | [CyberArkAudit_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit/Data%20Connectors/CyberArkAudit_API_FunctionApp.json) |

[→ View full connector details](../connectors/cyberarkaudit.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyberArkAudit` | [CyberArkAudit](../connectors/cyberarkaudit.md) |
| `CyberArk_AuditEvents_CL` | [CyberArkAudit](../connectors/cyberarkaudit.md) |

[← Back to Solutions Index](../solutions-index.md)
