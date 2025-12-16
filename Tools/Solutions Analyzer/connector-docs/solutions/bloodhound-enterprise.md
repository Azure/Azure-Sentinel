# BloodHound Enterprise

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | SpecterOps |
| **Support Tier** | Partner |
| **Support Link** | [https://bloodhoundenterprise.io/](https://bloodhoundenterprise.io/) |
| **Categories** | domains |
| **First Published** | 2023-05-04 |
| **Last Updated** | 2021-05-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BloodHound%20Enterprise](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BloodHound%20Enterprise) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Bloodhound Enterprise](../connectors/bloodhoundenterprise.md)

**Publisher:** SpecterOps

The solution is designed to test Bloodhound Enterprise package creation process.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **BloodHound Enterprise API key & Id** is required.  See the documentation to learn more about API on the `https://bloodhound.specterops.io/integrations/bloodhound-api/working-with-api`.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to a 'BloodHound Enterprise' to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

**STEP 1 - Retrieve BloodHound Enterprise API Key and ID**

To enable the Azure Function to authenticate successfully and pull logs into Microsoft Sentinel, you must first obtain the API Key and ID from your BloodHound Enterprise instance. See the documentation to learn more about API on the `https://bloodhound.specterops.io/integrations/bloodhound-api/working-with-api`.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the 'BloodHound Enterprise' connector, have the Workspace ID  and Workspace Primary Key (can be copied from the following), as well as the 'BloodHound Enterprise' API authorization key(s) or Token, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the 'BloodHound Enterprise' connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)]()
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Tenant URL**, **API Key**, **API ID** 'and/or Other required fields'. 
>Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**Option 2 - Manual Deployment of Azure Functions**

 Use the following step-by-step instructions to deploy the 'BloodHound Enterprise' connector manually with Azure Functions.

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
2. From terminal type **az functionapp deployment source config-zip -g <ResourceGroup> -n <FunctionApp> --src <Zip File>** and hit enter. Set the `ResourceGroup` value to: your resource group name. Set the `FunctionApp` value to: your newly created function app name. Set the `Zip File` value to: `digitalshadowsConnector.zip`(path to your zip file). Note:- Download the zip file from the link - [Function App Code](https://github.com/metron-labs/Azure-Sentinel/blob/bloodhound/Solutions/BloodHound/Data%20Connectors/BloodHoundAzureFunction.zip)

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

****STEP 3 - Register the Application in Microsoft Entra ID**

  1. **Open the [Microsoft Entra ID page](https://entra.microsoft.com/)**:
   - Click the provided link to open the **Microsoft Entra ID** registration page in a new tab.
   - Ensure you are logged in with an account that has **Admin level** permissions.

2. **Create a New Application**:
   - In the **Microsoft Entra ID portal**, select **App registrations** mentioned on the left-hand side tab.
   - Click on **+ New registration**.
   - Fill out the following fields:
     - **Name**: Enter a name for the app (e.g., “BloodHound App”).
     - **Supported account types**: Choose **Accounts in this organizational directory only** (Default Directory only - Single tenant).
     - **Redirect URI**: Leave this blank unless required otherwise.
   - Click **Register** to create the application.

3. **Copy Application and Tenant IDs**:
   - Once the app is registered, note the **Application (client) ID** and **Directory (tenant) ID** from the **Overview** page. You’ll need these for the integration.

4. **Create a Client Secret**:
   - In the **Certificates & secrets** section, click **+ New client secret**.
   - Add a description (e.g., 'BloodHound Secret') and set an expiration (e.g., 1 year).
   - Click **Add**.
   - **Copy the client secret value immediately**, as it will not be shown again.

  ****STEP 4 - Assign the "Monitoring Metrics Publisher" Role to the App**

  1. **Open the Resource Group in Azure Portal**:
   - Navigate to the **Resource Group** that contains the **Log Analytics Workspace** and **Data Collection Rules (DCRs)** where you want the app to push data.

2. **Assign the Role**:
   - In the **Resource Group** menu, click on **Access control (IAM)** mentioned on the left-hand side tab ..
   - Click on **+ Add** and select **Add role assignment**.
   - In the **Role** dropdown, search for and select the **Monitoring Metrics Publisher** role.
   - Under **Assign access to**, choose **Azure AD user, group, or service principal**.
   - In the **Select** field, search for your registered app by **name** or **client ID**.
   - Click **Save** to assign the role to the application.

  ****STEP 5 - Deploy the ARM Template**

  1. **Retrieve the Workspace ID**:
   - After assigning the role, you will need the **Workspace ID**.
   - Navigate to the **Log Analytics Workspace** within the **Resource Group**.
   - In the **Overview** section, locate the **Workspace ID** field under **Workspace details**.
   - **Copy the Workspace ID** and keep it handy for the next steps.

2. **Click the Deploy to Azure Button**:
   - [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmetron-labs%2FAzure-Sentinel%2Fbloodhound%2FSolutions%2FBloodHound%2FData%2520Connectors%2FDeployToAzure.json).
   - This will take you directly to the Azure portal to start the deployment.

3. **Review and Customize Parameters**:
   - On the custom deployment page, ensure you’re deploying to the correct **subscription** and **resource group**.
   - Fill in the parameters like **workspace name**, **workspace ID**, and **workspace location**.

4. **Click Review + Create** and then **Create** to deploy the resources.

  ****STEP 6 - Verify DCE, DCR, and Log Analytics Table Setup**

  1. **Check the Data Collection Endpoint (DCE)**:
   - After deploying, go to **Azure Portal > Data Collection Endpoints**.
   - Verify that the **BloodHoundDCE** endpoint has been created successfully.
   - **Copy the DCE Logs Ingestion URI**, as you’ll need this for generating the webhook URL.

2. **Confirm Data Collection Rule (DCR) Setup**:
   - Go to **Azure Portal > Data Collection Rules**.
   - Ensure the **BloodHoundDCR** rule is present.
   - **Copy the Immutable ID** of the DCR from the Overview page, as you’ll need it for the webhook URL.

3. **Validate Log Analytics Table**:
   - Navigate to your **Log Analytics Workspace** (linked to Microsoft Sentinel).
   - Under the **Tables** section, verify that the **BloodHoundTable_CL** table has been created successfully and is ready to receive data.

| | |
|--------------------------|---|
| **Tables Ingested** | `BHEAttackPathsData_CL` |
| **Connector Definition Files** | [BloodHoundFunction.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BloodHound%20Enterprise/Data%20Connectors/BloodHoundFunction.json) |

[→ View full connector details](../connectors/bloodhoundenterprise.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BHEAttackPathsData_CL` | [Bloodhound Enterprise](../connectors/bloodhoundenterprise.md) |

[← Back to Solutions Index](../solutions-index.md)
