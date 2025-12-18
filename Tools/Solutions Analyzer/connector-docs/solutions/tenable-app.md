# Tenable App

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Tenable |
| **Support Tier** | Partner |
| **Support Link** | [https://www.tenable.com/support/technical-support](https://www.tenable.com/support/technical-support) |
| **Categories** | domains |
| **First Published** | 2024-06-06 |
| **Last Updated** | 2025-06-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Tenable Identity Exposure](../connectors/tenableie.md)

**Publisher:** Tenable

### [Tenable Vulnerability Management](../connectors/tenablevm.md)

**Publisher:** Tenable

The TVM data connector provides the ability to ingest Asset, Vulnerability, Compliance, WAS assets and WAS vulnerabilities data into Microsoft Sentinel using TVM REST APIs. Refer to [API documentation](https://developer.tenable.com/reference) for more information. The connector provides the ability to get data which helps to examine potential security risks, get insight into your computing assets, diagnose configuration problems and more

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: Both a **TenableAccessKey** and a **TenableSecretKey** is required to access the Tenable REST API. [See the documentation to learn more about API](https://developer.tenable.com/reference#vulnerability-management). Check all [requirements and follow  the instructions](https://docs.tenable.com/vulnerability-management/Content/Settings/my-account/GenerateAPIKey.htm) for obtaining credentials.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Durable Functions to connect to the TenableVM API to pull [assets](https://developer.tenable.com/reference#exports-assets-download-chunk), [vulnerabilities](https://developer.tenable.com/reference#exports-vulns-request-export) and [compliance](https://developer.tenable.com/reference#exports-compliance-request-export)(if selected) at a regular interval into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This data connector depends on a [**TenableVM parser for vulnerabilities**](https://aka.ms/sentinel-TenableApp-TenableVMVulnerabilities-parser) and a [**TenableVM parser for assets**](https://aka.ms/sentinel-TenableApp-TenableVMAssets-parser) based on a Kusto Function to work as expected which is deployed with the Microsoft Sentinel Solution.

**STEP 1 - Configuration steps for TenableVM**

 [Follow the instructions](https://docs.tenable.com/vulnerability-management/Content/Settings/my-account/GenerateAPIKey.htm) to obtain the required API credentials.

**STEP 2 - App Registration steps for the Application in Microsoft Entra ID**

 This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:
 1. Sign in to the [Azure portal](https://portal.azure.com/).
 2. Search for and select **Microsoft Entra ID**.
 3. Under **Manage**, select **App registrations > New registration**.
 4. Enter a display **Name** for your application.
 5. Select **Register** to complete the initial app registration.
 6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the **Application (client) ID** and **Tenant ID**. The client ID and Tenant ID is required as configuration parameters for the execution of TenableVM Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)

**STEP 3 - Add a client secret for application in Microsoft Entra ID**

 Sometimes called an application password, a client secret is a string value required for the execution of TenableVM Data Connector. Follow the steps in this section to create a new Client Secret:
 1. In the Azure portal, in **App registrations**, select your application.
 2. Select **Certificates & secrets > Client secrets > New client secret**.
 3. Add a description for your client secret.
 4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
 5. Select **Add**. 
 6. *Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page.* The secret value is required as configuration parameter for the execution of TenableVM Data Connector. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret)

**STEP 4 - Get Object ID of your application in Microsoft Entra ID**

 After creating your app registration, follow the steps in this section to get Object ID:
 1. Go to **Microsoft Entra ID**.
 2. Select **Enterprise applications** from the left menu.
 3. Find your newly created application in the list (you can search by the name you provided).
 4. Click on the application.
 5. On the overview page, copy the **Object ID**. This is the **AzureEntraObjectId** needed for your ARM template role assignment.

**STEP 5 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function App**

**6. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the TenableVM Vulnerability Management Report data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-TenableVM-azuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-TenableVM-azuredeploy-gov)
2. Select the preferred **Subscription**, **Resource Group**, **FunctionApp Name** and **Location**. 
3. Enter the below information :  

	 a. **WorkspaceName** - Enter the Workspace Name of the log analytics Workspace. 

	 b. **TenableAccessKey** - Enter Access key for using the Tenable API. 

	 c. **TenableSecretKey** - Enter Tenable Secret Key for Authentication. 

	 d. **AzureClientID** - Enter Azure Client ID. 

	 e. **AzureClientSecret** - Enter Azure Client Secret. 

	 f. **TenantID** - Enter Tenant ID got from above steps. 

	 g. **AzureEntraObjectId** - Enter Azure Object ID got from above steps. 

	 h. **LowestSeveritytoStore** - Lowest vulnerability severity to store. Allowed Values: Info, Low, Medium, High, Critical. Default is Info. 

	 i. **ComplianceDataIngestion** - Select true if you want to enable Compliance data ingestion from Tenable VM. Default is false. 

	 j. **WASAssetDataIngestion** - Select true if you want to enable WAS Asset data ingestion from Tenable VM. Default is false. 

	 k. **WASVulnerabilityDataIngestion** - Select true if you want to enable WAS Vulnerability data ingestion from Tenable VM. Default is false. 

	 l. **LowestSeveritytoStoreWAS** - The Lowest Vulnerability severity to store for WAS. Allowed Values: Info, Low, Medium, High, Critical. Default is Info. 

	 m. **TenableExportScheduleInMinutes** - Schedule in minutes to create new export job from Tenable VM. Default is 1440. 

	 n. **AssetTableName** - Enter name of the table used to store Asset Data logs. 

	 o. **VulnTableName** - Enter name of the table used to store Vulnerability Data logs. 

	 p. **ComplianceTableName** - Enter name of the table used to store Compliance Data logs. 

	 q. **WASAssetTableName** - Enter name of the table used to store WAS Asset Data logs. 

	 r. **WASVulnTableName** - Enter name of the table used to store WAS Vulnerability Data logs. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**7. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the TenableVM Vulnerability Management Report data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-TenableVMAzureSentinelConnector310Updated-functionapp) file. Extract archive to your local development computer.
2. Start VS Code. Choose File in the main menu and select Open Folder.
3. Select the top level folder from extracted files.
4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.
If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**
If you're already signed in, go to the next step.
5. Provide the following information at the prompts:

	a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription:** Choose the subscription to use.

	c. Select **Create new Function App in Azure** (Don't choose the Advanced option)

	d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. TenableVMXXXXX).

	e. **Select a runtime:** Choose Python 3.12.

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
7. Go to Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **New application setting**.
3. Add each of the following application settings individually, with their respective string values (case-sensitive): 

	 a. **WorkspaceName** - Enter the Workspace Name of the log analytics Workspace. 

	 b. **TenableAccessKey** - Enter Access key for using the Tenable API. 

	 c. **TenableSecretKey** - Enter Tenable Secret Key for Authentication. 

	 d. **AzureClientID** - Enter Azure Client ID. 

	 e. **AzureClientSecret** - Enter Azure Client Secret. 

	 f. **TenantID** - Enter Tenant ID got from above steps. 

	 g. **AzureEntraObjectId** - Enter Azure Object ID got from above steps. 

	 h. **LowestSeveritytoStore** - Lowest vulnerability severity to store. Allowed Values: Info, Low, Medium, High, Critical. Default is Info. 

	 i. **ComplianceDataIngestion** - Select true if you want to enable Compliance data ingestion from Tenable VM. Default is false. 

	 j. **WASAssetDataIngestion** - Select true if you want to enable WAS Asset data ingestion from Tenable VM. Default is false. 

	 k. **WASVulnerabilityDataIngestion** - Select true if you want to enable WAS Vulnerability data ingestion from Tenable VM. Default is false. 

	 l. **LowestSeveritytoStoreWAS** - The Lowest Vulnerability severity to store for WAS. Allowed Values: Info, Low, Medium, High, Critical. Default is Info. 

	 m. **TenableExportScheduleInMinutes** - Schedule in minutes to create new export job from Tenable VM. Default is 1440. 

	 n. **AssetTableName** - Enter name of the table used to store Asset Data logs. 

	 o. **VulnTableName** - Enter name of the table used to store Vulnerability Data logs. 

	 p. **ComplianceTableName** - Enter name of the table used to store Compliance Data logs. 

	 q. **WASAssetTableName** - Enter name of the table used to store WAS Asset Data logs. 

	 r. **WASVulnTableName** - Enter name of the table used to store WAS Vulnerability Data logs. 

	 s. **PyTenableUAVendor** - Value must be set to **Microsoft**. 

	 t. **PyTenableUAProduct** - Value must be set to **Azure Sentinel**. 

	 u. **PyTenableUABuild** - Value must be set to **0.0.1**.
3. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `Tenable_VM_Asset_CL` |
| | `Tenable_VM_Compliance_CL` |
| | `Tenable_VM_Vuln_CL` |
| | `Tenable_WAS_Asset_CL` |
| | `Tenable_WAS_Vuln_CL` |
| **Connector Definition Files** | [TenableVM.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Data%20Connectors/TenableVM/TenableVM.json) |

[→ View full connector details](../connectors/tenablevm.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Tenable_IE_CL` | [Tenable Identity Exposure](../connectors/tenableie.md) |
| `Tenable_VM_Asset_CL` | [Tenable Vulnerability Management](../connectors/tenablevm.md) |
| `Tenable_VM_Compliance_CL` | [Tenable Vulnerability Management](../connectors/tenablevm.md) |
| `Tenable_VM_Vuln_CL` | [Tenable Vulnerability Management](../connectors/tenablevm.md) |
| `Tenable_WAS_Asset_CL` | [Tenable Vulnerability Management](../connectors/tenablevm.md) |
| `Tenable_WAS_Vuln_CL` | [Tenable Vulnerability Management](../connectors/tenablevm.md) |

[← Back to Solutions Index](../solutions-index.md)
