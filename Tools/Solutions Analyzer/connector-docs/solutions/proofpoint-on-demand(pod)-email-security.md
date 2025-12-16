# Proofpoint On demand(POD) Email Security

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Proofpoint, Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://proofpoint.my.site.com/community/s/](https://proofpoint.my.site.com/community/s/) |
| **Categories** | domains |
| **First Published** | 2021-03-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md)

**Publisher:** Proofpoint

### [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md)

**Publisher:** Proofpoint

Proofpoint On Demand Email Security data connector provides the capability to get Proofpoint on Demand Email Protection data, allows users to check message traceability, monitoring into email activity, threats,and data exfiltration by attackers and malicious insiders. The connector provides ability to review events in your org on an accelerated basis, get event log files in hourly increments for recent activity.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Websocket API Credentials/permissions**: **ProofpointClusterID**, **ProofpointToken** is required. [See the documentation to learn more about API](https://proofpointcommunities.force.com/community/s/article/Proofpoint-on-Demand-Pod-Log-API).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Proofpoint Websocket API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>This data connector depends on a parser based on a Kusto Function to work as expected. [Follow these steps](https://aka.ms/sentinel-proofpointpod-parser) to create the Kusto functions alias, **ProofpointPOD**

**STEP 1 - Configuration steps for the Proofpoint Websocket API**

1. Proofpoint Websocket API service requires Remote Syslog Forwarding license. Please refer the [documentation](https://proofpointcommunities.force.com/community/s/article/Proofpoint-on-Demand-Pod-Log-API) on how to enable and check PoD Log API. 
2. You must provide your cluster id and security token.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Proofpoint On Demand Email Security data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Proofpoint POD Log API credentials, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Proofpoint On Demand Email Security data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-proofpointpod-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **ProofpointClusterID**, **ProofpointToken** and deploy. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Proofpoint On Demand Email Security data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> NOTE:You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-proofpointpod-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. ProofpointXXXXX).

	e. **Select a runtime:** Choose Python 3.11.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive): 
		ProofpointClusterID
		ProofpointToken
		WorkspaceID
		WorkspaceKey
		logAnalyticsUri (optional)
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
3. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `ProofpointPODMessage_CL` |
| | `ProofpointPOD_maillog_CL` |
| | `ProofpointPOD_message_CL` |
| | `maillog_CL` |
| **Connector Definition Files** | [ProofpointPOD_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Data%20Connectors/ProofpointPOD_API_FunctionApp.json) |

[→ View full connector details](../connectors/proofpointpod.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ProofpointPODMailLog_CL` | [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md) |
| `ProofpointPODMessage_CL` | [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md), [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |
| `ProofpointPOD_maillog_CL` | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |
| `ProofpointPOD_message_CL` | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |
| `maillog_CL` | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |

[← Back to Solutions Index](../solutions-index.md)
