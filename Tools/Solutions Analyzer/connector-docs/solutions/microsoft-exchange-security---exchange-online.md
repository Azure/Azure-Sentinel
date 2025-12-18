# Microsoft Exchange Security - Exchange Online

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-12-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Exchange Security Insights Online Collector](../connectors/esi-exchangeonlinecollector.md)

**Publisher:** Microsoft

Connector used to push Exchange Online Security configuration for Microsoft Sentinel Analysis

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **microsoft.automation/automationaccounts permissions**: Read and write permissions to create an Azure Automation with a Runbook is required. [See the documentation to learn more about Automation Account](https://learn.microsoft.com/en-us/azure/automation/overview).
- **Microsoft.Graph permissions**: Groups.Read, Users.Read and Auditing.Read permissions are required to retrieve user/group information linked to Exchange Online assignments. [See the documentation to learn more](https://aka.ms/sentinel-ESI-OnlineCollectorPermissions).
- **Exchange Online permissions**: Exchange.ManageAsApp permission and **Global Reader** or **Security Reader** Role are needed to retrieve the Exchange Online Security Configuration.[See the documentation to learn more](https://aka.ms/sentinel-ESI-OnlineCollectorPermissions).
- **(Optional) Log Storage permissions**: Storage Blob Data Contributor to a storage account linked to the Automation Account Managed identity or an Application ID is mandatory to store logs.[See the documentation to learn more](https://aka.ms/sentinel-ESI-OnlineCollectorPermissions).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE - UPDATE**

ℹ️ <H1><b><u>NOTE - UPDATE:</u></b></H1>We recommend to Update the Collector to Version <b>7.6.0.0</b> or highier. <br/>The Collector Script Update procedure could be found here : <a href='https://aka.ms/sentinel-ESI-OnlineCollectorUpdate'>ESI Online Collector Update</a>

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected. Follow the steps for each Parser to create the Kusto Functions alias : [**ExchangeConfiguration**](https://aka.ms/sentinel-ESI-ExchangeConfiguration-Online-parser) and [**ExchangeEnvironmentList**](https://aka.ms/sentinel-ESI-ExchangeEnvironmentList-Online-parser) 

**STEP 1 - Parsers deployment**
**Parser deployment (When using Microsoft Exchange Security Solution, Parsers are automatically deployed)**

**1. Download the Parser files**

  The latest version of the 2 files [**ExchangeConfiguration.yaml**](https://aka.ms/sentinel-ESI-ExchangeConfiguration-Online-parser) and [**ExchangeEnvironmentList.yaml**](https://aka.ms/sentinel-ESI-ExchangeEnvironmentList-Online-parser)

  **2. Create Parser **ExchangeConfiguration** function**

  In 'Logs' explorer of your Microsoft Sentinel's log analytics, copy the content of the file to Log explorer

  **3. Save Parser **ExchangeConfiguration** function**

  Click on save button.
 Define the parameters as asked on the header of the parser file.
Click save again.

  **4. Reproduce the same steps for Parser **ExchangeEnvironmentList****

  Reproduce the step 2 and 3 with the content of 'ExchangeEnvironmentList.yaml' file

>**NOTE:** This connector uses Azure Automation to connect to 'Exchange Online' to pull its Security analysis into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Automation pricing page](https://azure.microsoft.com/pricing/details/automation/) for details.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Automation**

>**IMPORTANT:** Before deploying the 'ESI Exchange Online Security Configuration' connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Exchange Online tenant name (contoso.onmicrosoft.com), readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the 'ESI Exchange Online Security Configuration' connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-ExchangeCollector-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **Tenant Name**, 'and/or Other required fields'. 
>4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**Option 2 - Manual Deployment of Azure Automation**

 Use the following step-by-step instructions to deploy the 'ESI Exchange Online Security Configuration' connector manually with Azure Automation.
**A. Create the Azure Automation Account**

  1.  From the Azure Portal, navigate to [Azure Automation Account](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Automation%2FAutomationAccounts).
2. Click **+ Add** at the top.
3. In the **Basics** tab, fill the required fields and give a name to the Azure Automation. 
4. In the **Advanced** and **Networking** and **Tags** Tabs, leave fields as default if you don't need to customize them.
5. 'Make other preferable configuration changes', if needed, then click **Create**.

  **B. Add Exchange Online Management Module, Microsoft Graph (Authentication, User and Group) Modules**

  1. On the Automation Account page, select **Modules**.
2. Click on **Browse gallery** and search the **ExchangeOnlineManagement** module.
3. Select it and click on **Select**.
4. Choose Version **5.1** on Runtime version field and click on Import button.
Repeat the step for the following modules : 'Microsoft.Graph.Authentication', 'Microsoft.Graph.Users' and 'Microsoft.Graph.Groups. **Attention, you need to wait for Microsoft.Graph.Authentication installation before processing next modules**

  **C. Download the Runbook Content**

  1. Download the latest version of ESI Collector. The latest version can be found here : https://aka.ms/ESI-ExchangeCollector-Script
2. Unzip the file to find the JSON file and the PS1 file for next step.

  **D. Create Runbook**

  1. On the Automation Account page, select the **Runbooks** button.
2. Click on **Create a runbook** and name it like 'ESI-Collector' with a runbook type **PowerShell**, Runtime Version **5.1** and click 'Create'.
2. Import the content of the previous step's PS1 file in the Runbook window.
3. Click on **Publish**

  **E. Create GlobalConfiguration Variable**

  1. On the Automation Account page, select the **Variables** button.
2. Click on **Add a Variable** and name it exaclty 'GlobalConfiguration' with a type **String**.
2. On 'Value' field, copy the content of the previous step's JSON file.
3. Inside the content, replace the values of **WorkspaceID** and **WorkspaceKey**.
4. Click on 'Create' button.

  **F. Create TenantName Variable**

  1. On the Automation Account page, select the **Variables** button.
2. Click on **Add a Variable** and name it exaclty 'TenantName' with a type **String**.
3. On 'Value' field, write the tenant name of your Exchange Online.
4. Click on 'Create' button.

  **G. Create LastDateTracking Variable**

  1. On the Automation Account page, select the **Variables** button.
2. Click on **Add a Variable** and name it exaclty 'LastDateTracking' with a type **String**.
3. On 'Value' field, write 'Never'.
4. Click on 'Create' button.

  **H. Create a Runbook Schedule**

  1. On the Automation Account page, select the **Runbook** button and click on your created runbook.
2. Click on **Schedules** and **Add a schedule** button.
3. Click on **Schedule**, **Add a Schedule** and name it. Select **Recurring** value with a reccurence of every 1 day, click 'Create'.
4. Click on 'Configure parameters and run settings'. Leave all empty and click on **OK** and **OK** again.

**STEP 3 - Assign Microsoft Graph Permission and Exchange Online Permission to Managed Identity Account** 

To be able to collect Exchange Online information and to be able to retrieve User information and memberlist of admin groups, the automation account need multiple permission.
**Assign Permissions by Script**

**A. Download Permission Script**

  [Permission Update script](https://aka.ms/ESI-ExchangeCollector-Permissions)

  **B. Retrieve the Azure Automation Managed Identity GUID and insert it in the downloaded script**

  1. Go to your Automation Account, in the **Identity** Section. You can find the Guid of your Managed Identity.
2. Replace the GUID in $MI_ID = "XXXXXXXXXXX" with the GUID of your Managed Identity.

  **C. Launch the script with a **Global-Administrator** account**

  **Attention this script requires MSGraph Modules and Admin Consent to access to your tenant with Microsoft Graph**.
	The script will add 3 permissions to the Managed identity:
	1. Exchange Online ManageAsApp permission
	2. User.Read.All on Microsoft Graph API
	3. Group.Read.All on Microsoft Graph API

  **D. Exchange Online Role Assignment**

  1. As a **Global Administrator**, go to **Roles and Administrators**.
2. Select **Global Reader** role or **Security Reader** and click to 'Add assignments'.
3. Click on 'No member selected' and search your Managed Identity account Name beginning by **the name of your automation account** like 'ESI-Collector'. Select it and click on 'Select'.
4. Click **Next** and validate the assignment by clicking **Assign**.

| | |
|--------------------------|---|
| **Tables Ingested** | `ESIExchangeOnlineConfig_CL` |
| **Connector Definition Files** | [ESI-ExchangeOnlineCollector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Data%20Connectors/ESI-ExchangeOnlineCollector.json) |

[→ View full connector details](../connectors/esi-exchangeonlinecollector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ESIExchangeOnlineConfig_CL` | [Exchange Security Insights Online Collector](../connectors/esi-exchangeonlinecollector.md) |

[← Back to Solutions Index](../solutions-index.md)
